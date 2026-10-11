"""Application service: the only entry point the API uses to drive the workflow.

Responsibilities: authorisation, single-run-per-proposal concurrency, translating user
actions into graph inputs or ``Command(resume=...)``, background execution, and syncing
the durable proposal record from the checkpointed workflow state.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Any

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from src.checkpoints import thread_config, is_interrupted_by_error, pending_interrupt
from src.domain.proposal_record import RunState
from src.routing import N
from src.shared import WorkflowStage, ApprovalStatus, ApprovalDecision
from src.shared.models import RequirementsSpecification, TechnicalProposal, FinancialEstimate, DocumentMetadata, \
    WorkflowStatus
from src.repositories.proposal_repository import ProposalRecord, ProposalRepository
from src.services.version_service import stale_artifacts
from src.utils.logging import get_logger, proposal_id_var, redact
from src.state.state import get_requirements, get_technical, get_estimate, get_approval, get_document

log = get_logger(__name__)


class ServiceError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(ServiceError):
    status_code = 404
    code = "not_found"


class ConflictError(ServiceError):
    status_code = 409
    code = "conflict"


class ForbiddenError(ServiceError):
    status_code = 403
    code = "forbidden"


@dataclass
class Principal:
    user_id: str
    is_admin: bool = False


@dataclass
class ProposalView:
    record: ProposalRecord
    requirements: RequirementsSpecification | None
    technical: TechnicalProposal | None
    estimate: FinancialEstimate | None
    document: DocumentMetadata | None
    stale: list[str]
    interrupt: dict[str, Any] | None
    errors: list[str]


class ProposalService:
    def __init__(self, graph: CompiledStateGraph, repo: ProposalRepository) -> None:
        self._graph = graph
        self._repo = repo
        self._tasks: set[asyncio.Task[None]] = set()

    # ---- authorisation -------------------------------------------------------------
    async def _authorized(self, principal: Principal, proposal_id: str) -> ProposalRecord:
        record = await self._repo.get_proposal(proposal_id)
        # Same response for "missing" and "not yours" to avoid leaking existence.
        if record is None or (record.owner_id != principal.user_id and not principal.is_admin):
            raise NotFoundError("Proposal not found")
        return record

    # ---- execution -------------------------------------------------------------------
    async def _launch(self, rec: ProposalRecord, graph_input: Any, wait: bool) -> None:
        if not await self._repo.try_start_run(rec.proposal_id):
            raise ConflictError("The workflow is already processing a request for this proposal")
        await self._repo.update_proposal(rec.proposal_id, workflow_status=WorkflowStatus.RUNNING, last_error=None)
        task = asyncio.create_task(self._execute(rec, graph_input))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        if wait:
            await task

    async def _execute(self, rec: ProposalRecord, graph_input: Any) -> None:
        proposal_id_var.set(rec.proposal_id)
        try:
            await self._graph.ainvoke(graph_input, thread_config(rec.thread_id))
            await self._sync_record(rec)
            await self._repo.finish_run(rec.proposal_id, RunState.IDLE)
        except Exception as exc:
            log.exception("Workflow run failed")
            message = redact(f"{type(exc).__name__}: {exc}")[:500]
            await self._repo.finish_run(rec.proposal_id, RunState.FAILED, message)
            await self._repo.update_proposal(rec.proposal_id, workflow_status=WorkflowStatus.FAILED)
            await self._repo.add_message(
                rec.proposal_id, "assistant",
                "Something went wrong while processing this step. Your progress is saved — use Resume to retry.",
                "error",
            )

    async def _sync_record(self, record: ProposalRecord) -> None:
        snap = await self._graph.aget_state(thread_config(record.thread_id))
        v = snap.values or {}
        await self._repo.update_proposal(
            record.proposal_id,
            workflow_status=WorkflowStatus(v.get("workflow_status", WorkflowStatus.RUNNING)),
            current_stage=WorkflowStage(v.get("current_stage", WorkflowStage.REQUIREMENTS)),
            pending_questions=v.get("pending_questions") or [],
            approval_status=ApprovalStatus(v.get("approval_status", ApprovalStatus.NOT_REQUESTED)),
            revision_number=int(v.get("revision_number", 0)),
            customer_name=v.get("customer_name") or record.customer_name
                          or ((v.get("requirements_state") or {}).get("spec") or {}).get("customer_name", ""),
        )

    async def drain(self) -> None:
        """Wait for background runs (used on shutdown and in tests)."""
        if self._tasks:
            await asyncio.gather(*list(self._tasks), return_exceptions=True)

    # ---- commands --------------------------------------------------------------------
    async def create(self, principal: Principal, title: str, customer_name: str, message: str, wait: bool = False) -> ProposalRecord:
        pid = f"PRP-{uuid.uuid4().hex[:10].upper()}"
        rec = ProposalRecord(proposal_id=pid, owner_id=principal.user_id, title=title, customer_name=customer_name,
                             thread_id=f"thread-{pid}")
        await self._repo.create_proposal(rec)
        await self._repo.add_message(pid, "user", message)
        initial = {
            "proposal_id": pid, "thread_id": rec.thread_id, "user_id": principal.user_id, "title": title,
            "customer_name": customer_name, "incoming_message": message, "revision_number": 0,
            "artifact_versions": {}, "approval_status": ApprovalStatus.NOT_REQUESTED.value,
            "workflow_status": WorkflowStatus.RUNNING.value,
            "current_stage": WorkflowStage.REQUIREMENTS.value,
        }
        await self._launch(rec, initial, wait)
        return await self._repo.get_proposal(pid)

    async def send_message(self, principal: Principal, proposal_id: str, text: str, wait: bool = False) -> ProposalRecord:
        rec = await self._authorized(principal, proposal_id)
        self._ensure_not_running(rec)
        if rec.workflow_status == WorkflowStatus.CANCELLED:
            raise ConflictError("This proposal was cancelled; create a new proposal to continue")
        if await is_interrupted_by_error(self._graph, rec.thread_id):
            raise ConflictError("The previous step failed. Use resume to retry it before sending new messages")
        intr = await pending_interrupt(self._graph, rec.thread_id)
        graph_input: Any = Command(resume={"kind": "message", "text": text}) if intr else {"incoming_message": text}
        await self._repo.add_message(proposal_id, "user", text)
        await self._launch(rec, graph_input, wait)
        return await self._authorized(principal, proposal_id)

    async def decide(self, principal: Principal, proposal_id: str, decision: ApprovalDecision, feedback: str | None,
                     estimate_version: int, wait: bool = False) -> ProposalRecord:
        rec = await self._authorized(principal, proposal_id)
        self._ensure_not_running(rec)
        intr = await pending_interrupt(self._graph, rec.thread_id)
        if intr is None or intr.node != N.APPROVAL:
            raise ConflictError("No estimate is awaiting approval")
        current = int(intr.value.get("estimate_version", -1))
        if estimate_version != current:
            raise ConflictError(f"Estimate v{estimate_version} is stale; the current estimate is v{current}")
        if decision == ApprovalDecision.REQUEST_CHANGES and not (feedback or "").strip():
            raise ServiceError("Feedback is required when requesting changes")
        label = {"approve": "Approved", "reject": "Rejected", "request_changes": "Requested changes", "cancel": "Cancelled"}[decision.value]
        await self._repo.add_message(proposal_id, "user", f"{label} estimate v{estimate_version}" + (f": {feedback}" if feedback else ""), "decision")
        cmd = Command(resume={"kind": "approval", "decision": decision.value, "feedback": feedback,
                              "estimate_version": estimate_version, "user_id": principal.user_id})
        await self._launch(rec, cmd, wait)
        return await self._authorized(principal, proposal_id)

    async def resume(self, principal: Principal, proposal_id: str, action: str, wait: bool = False) -> ProposalRecord:
        rec = await self._authorized(principal, proposal_id)
        self._ensure_not_running(rec)
        if action == "cancel":
            intr = await pending_interrupt(self._graph, rec.thread_id)
            if intr is None:
                raise ConflictError("Nothing to cancel: the workflow is not paused")
            await self._launch(rec, Command(resume={"kind": "cancel"}), wait)
            return await self._authorized(principal, proposal_id)
        if await is_interrupted_by_error(self._graph, rec.thread_id):
            await self._launch(rec, None, wait)  # continue from the last successful checkpoint
            return await self._authorized(principal, proposal_id)
        intr = await pending_interrupt(self._graph, rec.thread_id)
        if intr is None:
            raise ConflictError("The workflow is not paused")
        if intr.node == N.APPROVAL:
            raise ConflictError("The estimate needs an explicit approval decision")
        await self._launch(rec, Command(resume={"kind": "retry"}), wait)
        return await self._authorized(principal, proposal_id)

    @staticmethod
    def _ensure_not_running(rec: ProposalRecord) -> None:
        if rec.run_state == RunState.RUNNING:
            raise ConflictError("The workflow is already processing a request for this proposal")

    # ---- queries ---------------------------------------------------------------------
    async def list(self, principal: Principal) -> list[ProposalRecord]:
        return await self._repo.list_proposals(None if principal.is_admin else principal.user_id)

    async def view(self, principal: Principal, proposal_id: str) -> ProposalView:
        rec = await self._authorized(principal, proposal_id)
        snap = await self._graph.aget_state(thread_config(rec.thread_id))
        v = snap.values or {}
        req, tp, est = get_requirements(v), get_technical(v), get_estimate(v)
        ap, doc = get_approval(v), get_document(v)
        intr = await pending_interrupt(self._graph, rec.thread_id)
        return ProposalView(
            record=rec, requirements=req, technical=tp, estimate=est, document=doc,
            stale=stale_artifacts(req, tp, est, ap, doc),
            interrupt={"node": intr.node, **intr.value} if intr else None,
            errors=list(v.get("errors") or [])[-5:],
        )

    async def messages(self, principal: Principal, proposal_id: str):
        await self._authorized(principal, proposal_id)
        return await self._repo.list_messages(proposal_id)

    async def versions(self, principal: Principal, proposal_id: str):
        await self._authorized(principal, proposal_id)
        return (
            await self._repo.list_artifacts(proposal_id),
            await self._repo.list_approvals(proposal_id),
            await self._repo.list_documents(proposal_id),
        )

    async def document(self, principal: Principal, proposal_id: str, version: int | None) -> DocumentMetadata:
        await self._authorized(principal, proposal_id)
        docs = await self._repo.list_documents(proposal_id)
        if not docs:
            raise NotFoundError("No approved document has been generated yet")
        if version is None:
            return docs[-1]
        for d in docs:
            if d.document_version == version:
                return d
        raise NotFoundError(f"Document version {version} not found")
