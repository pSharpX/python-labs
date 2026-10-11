import functools
import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt, Command

from config import serde
from settings import BaseModelSettings, ApplicationSettings
from src.agents import TechArchitectAgent, RequirementsScoutAgent, FinancialEstimatorAgent, PresentationAgent
from src.agents.requirements_scout_agent import RequirementsValidator
from src.repositories.proposal_repository import ProposalRepository
from src.routing import N, route_after_ingest, route_after_validation, READY_TARGETS, route_after_technical, \
    route_after_financial, route_after_approval, route_after_await
from src.services.document_service import _money, DocumentService
from src.services.financial_service import FinancialService
from src.services.version_service import requirements_fingerprint, VersionService, approval_for_estimate, \
    technical_fingerprint, estimate_fingerprint, approval_is_valid
from src.shared import WorkflowStatus, UserResponse, UserAction, WorkflowStage, PendingInput
from src.shared.enums import ArtifactType, ApprovalStatus, RequirementStatus, TechnicalStatus, EstimateStatus, \
    ApprovalDecision, DECISION_TO_STATUS
from src.shared.models import ChatTurn, ApprovalRecord
from src.state import WorkflowState
from src.state.financial_estimator import FinancialEstimatorAgentState
from src.state.presentation import PresentationAgentState
from src.state.requirements import RequirementsAgentState
from src.state.state import get_estimate, get_approval, get_technical, get_requirements
from src.tools.mcp import MCPToolsAdapter
from src.utils.hashing import utcnow
from .configs import langfuse_handler
from .state.architect import TechArchitectAgentState


logger = logging.getLogger(__name__)

Update = dict[str, Any]

def _error_update(state: WorkflowState, stage: WorkflowStage, message: str) -> Update:
    logger.error("[%s] %s", stage.value, message)
    return {
        "status": WorkflowStatus.FAILED,
        "current_stage": stage,
        "errors": [*state.get("errors", []), f"{stage.value}: {message}"],
    }

def guarded(stage: WorkflowStage) -> Callable[[Callable[..., Awaitable[Update]]], Callable[..., Awaitable[Update]]]:
    """Turn any failure of an agent node into ``status=ERROR`` + a stored error. Never continue silently."""

    def decorator(fn: Callable[..., Awaitable[Update]]) -> Callable[..., Awaitable[Update]]:
        @functools.wraps(fn)
        async def wrapper(self: "TechDocBuilderGraph", state: WorkflowState, config: RunnableConfig) -> Update:
            try:
                return await fn(self, state, config)
            except Exception as exc:
                logger.exception("Stage %s failed", stage.value)
                return _error_update(state, stage, f"{type(exc).__name__}: {exc}")

        return wrapper
    return decorator

@dataclass(frozen=True)
class WorkflowSnapshot:
    """What a caller (API, UI, CLI) needs to know after every step."""

    proposal_id: str
    values: dict[str, Any]
    interrupt: dict[str, Any] | None  # payload the human must answer, if paused

    @property
    def status(self) -> WorkflowStatus | None:
        return self.values.get("status")

    @property
    def waiting_for_user(self) -> bool:
        return self.interrupt is not None


class TechDocBuilderGraph:
    """A langgraph powered workflow that design and write technical-functional proposals and financial documents."""

    def __init__(
            self,
            mcp_adapter: MCPToolsAdapter,
            version_service: VersionService,
            validator: RequirementsValidator,
            proposal_repository: ProposalRepository,
            financial_service: FinancialService,
            document_service: DocumentService,
    ):
        self._app_settings = ApplicationSettings()
        self._model_settings = BaseModelSettings()
        self._model = init_chat_model(
            model=self._model_settings.model_name,
            model_provider=self._model_settings.provider,
            temperature=self._model_settings.temperature,
        )
        self._callbacks = [
            langfuse_handler
        ]
        self._builder = StateGraph(
            state_schema=WorkflowState,
        )
        self._validator = validator
        self._version_service = version_service
        self._proposal_repository = proposal_repository
        self._mcp_adapter = mcp_adapter

        # Initialize agents
        self._req_scout_agent = RequirementsScoutAgent()
        self._tech_architect_agent = TechArchitectAgent(
            mcp_adapter=self._mcp_adapter
        )
        self._financial_estimator_agent = FinancialEstimatorAgent(financial_service=financial_service)
        self._presentation_agent = PresentationAgent(document_service=document_service)

        # Initialize workflow
        self._graph: CompiledStateGraph = self._build()

    async def _say(self, state: WorkflowState, text: str, kind: str = "chat") -> None:
        await self._proposal_repository.add_message(state["proposal_id"], "assistant", text, kind)

    @staticmethod
    def _versions(state: WorkflowState, artifact: ArtifactType, version: int, fp: str,
                  based_on: dict[str, str] | None = None) -> dict[str, dict[str, Any]]:
        versions = dict(state.get("artifact_versions") or {})
        versions[artifact.value] = {"version": version, "fingerprint": fp, "based_on": based_on or {},
                                    "updated_at": utcnow().isoformat()}
        return versions

    @guarded(WorkflowStage.INITIALIZE)
    async def _initialize_proposal(self, state: WorkflowState, config: RunnableConfig):
        msg = state.get("incoming_message")
        update: dict[str, Any] = {"workflow_status": WorkflowStatus.RUNNING.value, "errors": []}
        if msg:
            update["conversation_history"] = [ChatTurn(role="user", content=msg).model_dump(mode="json")]
            if not state.get("user_request"):
                update["user_request"] = msg
            # A message after a rejection or change request is feedback for the estimate revision.
            est = get_estimate(state)
            if approval_for_estimate(est, get_approval(state)) in (ApprovalStatus.REJECTED,
                                                                   ApprovalStatus.CHANGES_REQUESTED):
                update["user_feedback"] = msg
        return update

    @guarded(WorkflowStage.REQUIREMENTS)
    async def _requirements_agent_node(self, state: WorkflowState, config: RunnableConfig):
        """Requirements-scout Node capture business requirements, objectives and define acceptance criteria."""

        raw = state.get("requirements_state")
        req_state = RequirementsAgentState.model_validate(raw) if raw else RequirementsAgentState(
            proposal_id=state["proposal_id"])
        msg = state.get("incoming_message") or ""
        req_state.conversation.append(ChatTurn(role="user", content=msg))
        req_state.latest_user_message = msg
        spec = await self._req_scout_agent.arun(req_state, config["configurable"], version=0)
        fp = requirements_fingerprint(spec)
        if req_state.spec is not None and fp == req_state.fingerprint:
            spec.version = req_state.spec.version
        else:
            spec.version = await self._version_service.next_version(state["proposal_id"], ArtifactType.REQUIREMENTS)
        req_state.spec, req_state.fingerprint = spec, fp
        return {
            "requirements_state": req_state.model_dump(mode="json"),
            "incoming_message": None,
            "current_stage": WorkflowStage.REQUIREMENTS.value,
        }

    @guarded(WorkflowStage.REQUIREMENTS)
    async def _requirements_validation(self, state: WorkflowState, config: RunnableConfig ) -> dict[str, Any]:
        req_state = RequirementsAgentState.model_validate(state["requirements_state"])
        assert req_state.spec is not None
        spec = self._validator.apply(req_state.spec)
        fp = requirements_fingerprint(spec)
        req_state.spec, req_state.fingerprint = spec, fp
        await self._version_service.record(state["proposal_id"], ArtifactType.REQUIREMENTS, spec, fp)
        update: dict[str, Any] = {
            "artifact_versions": self._versions(state, ArtifactType.REQUIREMENTS, spec.version, fp),
            "current_stage": WorkflowStage.REQUIREMENTS.value,
        }
        if spec.status != RequirementStatus.READY:
            questions = spec.client_questions
            reply = "Para preparar una propuesta precisa, necesito algunos detalles más:\n" + "\n".join(
                f"- {q}" for q in questions)
            req_state.conversation.append(ChatTurn(role="assistant", content=reply))
            await self._say(state, reply, "clarification")
            update.update(
                requirements_state=req_state.model_dump(mode="json"),
                pending_questions=questions,
                workflow_status=WorkflowStatus.AWAITING_USER.value,
                resume_stage=N.VALIDATION,
            )
            return update

        tech_state = get_technical(state)
        revision = state.get("revision_number", 0)
        if tech_state is not None and tech_state.based_on_requirements_fingerprint != fp:
            revision += 1
            stale = ["technical proposal", "financial estimate"]
            if get_approval(state) is not None:
                stale += ["approval", "final document"]
            await self._say(state,
                            f"Requerimientos actualizados a v{spec.version} ({spec.change_summary or 'Cambios registrados'}). "
                            f"Regenerating: {', '.join(stale)}.", "status")
        elif tech_state is None:
            await self._say(state, f"Requerimientos v{spec.version} están completos. Diseñando la solución técnica…",
                            "status")
        req_state.conversation.append(ChatTurn(role="assistant", content="Requerimientos confirmados como listos."))
        update.update(
            requirements_state=req_state.model_dump(mode="json"),
            pending_questions=[],
            revision_number=revision,
            workflow_status=WorkflowStatus.RUNNING.value,
        )
        return update

    @guarded(WorkflowStage.AWAIT_USER_INPUT)
    async def _awaiting_user_input(self, state: WorkflowState, config: RunnableConfig):
        payload = {
            "type": "user_input_required",
            "stage": state.get("current_stage"),
            "questions": state.get("pending_questions") or [],
            "resume_stage": state.get("resume_stage"),
        }
        response: dict[str, Any] = interrupt(payload)
        kind = response.get("kind")
        if kind == "message":
            return {"incoming_message": response.get("text", ""), "workflow_status": WorkflowStatus.RUNNING.value}
        if kind == "cancel":
            await self._say(state, "Workflow cancelled. History and artifacts are preserved.", "status")
            return {"workflow_status": WorkflowStatus.CANCELLED.value}
        # retry / continue: re-run the stage that blocked
        return {"workflow_status": WorkflowStatus.RUNNING.value}

    @guarded(WorkflowStage.TECHNICAL_ARCHITECTURE)
    async def _tech_architect_agent_node(self, state: WorkflowState, config: RunnableConfig):
        """Technical Architect Node design and implement the technical solution based on functional requirements."""
        req = get_requirements(state)
        assert req is not None and req.status == RequirementStatus.READY, "requirements must be ready"
        req_fp = requirements_fingerprint(req)
        version = await self._version_service.next_version(state["proposal_id"], ArtifactType.TECHNICAL_PROPOSAL)
        tech_state = TechArchitectAgentState(proposal_id=state["proposal_id"], requirements=req,
                                     requirements_fingerprint=req_fp)
        tech_state = await self._tech_architect_agent.arun(tech_state, config, version)
        tp = tech_state.output
        assert tp is not None
        fp = technical_fingerprint(tp)
        tech_state.fingerprint = fp
        await self._version_service.record(state["proposal_id"], ArtifactType.TECHNICAL_PROPOSAL, tp, fp,
                                     {ArtifactType.REQUIREMENTS.value: req_fp})
        update: dict[str, Any] = {
            "technical_architecture_state": tech_state.model_dump(mode="json"),
            "artifact_versions": self._versions(state, ArtifactType.TECHNICAL_PROPOSAL, tp.version, fp,
                                                {ArtifactType.REQUIREMENTS.value: req_fp}),
            "current_stage": WorkflowStage.TECHNICAL_ARCHITECTURE.value,
        }
        if tp.status == TechnicalStatus.READY:
            svc = tp.requested_service.catalog_service_option if tp.requested_service else "—"
            await self._say(state,
                            f"Propuesta técnica v{tp.version} completa: {svc}, {len(tp.implementation_phases)} fases, "
                            f"{tp.timeline_estimation.total_duration_weeks if tp.timeline_estimation else '?'} semanas. Estimando esfuerzo y costo…",
                            "status")
            update["workflow_status"] = WorkflowStatus.RUNNING.value
        else:
            questions = [q.question for q in tp.open_questions if q.blocking] or tp.validation_issues
            label = "needs clarification" if tp.status == TechnicalStatus.NEEDS_CLARIFICATION else "could not be completed"
            await self._say(state, f"The technical design {label}:\n" + "\n".join(f"- {q}" for q in questions)
                            + "\nResponde con los detalles faltantes o usa Reanudar para reintentar.", "clarification")
            update.update(pending_questions=questions, workflow_status=WorkflowStatus.AWAITING_USER.value,
                          resume_stage=N.ARCHITECT)
        return update

    @guarded(WorkflowStage.FINANCIAL_ESTIMATION)
    async def _financial_estimator_agent_node(self, state: WorkflowState, config: RunnableConfig):
        """Financial Estimator Node calculate the effort, the cost and commercial conditions."""

        tp = get_technical(state)
        assert tp is not None and tp.status == TechnicalStatus.READY, "technical proposal must be ready"
        tp_fp = technical_fingerprint(tp)
        prev = get_estimate(state)
        feedback = state.get("user_feedback")
        version = await self._version_service.next_version(state["proposal_id"], ArtifactType.FINANCIAL_ESTIMATE)
        fs = FinancialEstimatorAgentState(proposal_id=state["proposal_id"], technical=tp, technical_fingerprint=tp_fp,
                                     feedback=feedback, previous_estimate_version=prev.version if prev else None)
        fs = await self._financial_estimator_agent.arun(fs, version)

        # Scope-changing feedback goes back upstream once; if requirements absorb it without
        # change, the second pass treats it as an effort revision (prevents loops).
        if fs.scope_change_detected and feedback and not state.get("scope_redirected"):
            await self._say(state, "Your feedback changes the technical scope, so I'm updating the requirements first.",
                            "status")
            return {"incoming_message": f"[Change requested during estimate review] {feedback}", "user_feedback": None,
                    "scope_redirected": True, "current_stage": WorkflowStage.FINANCIAL_ESTIMATION.value}

        est = fs.output
        assert est is not None
        fp = estimate_fingerprint(est)
        fs.fingerprint = fp
        based = {ArtifactType.TECHNICAL_PROPOSAL.value: tp_fp}
        update: dict[str, Any] = {
            "financial_estimate_state": fs.model_dump(mode="json"),
            "artifact_versions": self._versions(state, ArtifactType.FINANCIAL_ESTIMATE, est.version, fp, based),
            "current_stage": WorkflowStage.FINANCIAL_ESTIMATION.value,
            "user_feedback": None,
            "scope_redirected": False,
        }
        if est.status == EstimateStatus.INVALID:
            await self._version_service.record(state["proposal_id"], ArtifactType.FINANCIAL_ESTIMATE, est, fp, based)
            await self._say(state, "The estimate could not be validated:\n" + "\n".join(
                f"- {e}" for e in est.validation_errors)
                            + "\nFix the configuration or reply with details, then Resume.", "clarification")
            update.update(pending_questions=est.validation_errors, workflow_status=WorkflowStatus.AWAITING_USER.value,
                          resume_stage=N.FINANCIAL, approval_status=ApprovalStatus.NOT_REQUESTED.value)
            return update

        # Persist the estimate before pausing for approval.
        est.approval_status = ApprovalStatus.PENDING
        fs.output = est
        update["financial_estimate_state"] = fs.model_dump(mode="json")
        await self._version_service.record(state["proposal_id"], ArtifactType.FINANCIAL_ESTIMATE, est, fp, based)
        await self._say(state,
                        f"Estimate v{est.version} ready for your approval: {_money(est.total_cost, est.currency)} "
                        f"for {est.total_hours:g} hours over {est.estimated_duration or 'the planned duration'}.",
                        "approval")
        update.update(approval_status=ApprovalStatus.PENDING.value,
                      workflow_status=WorkflowStatus.AWAITING_APPROVAL.value,
                      pending_questions=[], resume_stage=N.APPROVAL)
        return update

    @guarded(WorkflowStage.DOCUMENT_GENERATION)
    async def _document_generator_agent_node(self, state: WorkflowState, config: RunnableConfig):
        """Presentation Agent"""

        req, tp, est, ap = get_requirements(state), get_technical(state), get_estimate(state), get_approval(state)
        if not approval_is_valid(req, tp, est, ap):
            raise RuntimeError("Presentation requires a current approval of the current estimate")
        assert req and tp and est
        docs = await self._proposal_repository.list_documents(state["proposal_id"])
        ps = PresentationAgentState(
            proposal_id=state["proposal_id"], title=state.get("title") or "Technical-Functional Proposal",
            customer_name=state.get("customer_name") or req.customer_name, requirements=req, technical=tp,
            estimate=est, approval=ap,
        )
        ps = await self._presentation_agent.arun(ps, config=config, document_version=len(docs) + 1)
        assert ps.document is not None
        await self._proposal_repository.save_document(ps.document)
        await self._version_service.record(state["proposal_id"], ArtifactType.DOCUMENT, ps.document, ps.document.content_hash,
                                     {ArtifactType.FINANCIAL_ESTIMATE.value: estimate_fingerprint(est)})
        await self._say(state, f"Proposal document v{ps.document.document_version} is ready to download.", "document")
        return {
            "presentation_state": ps.model_dump(mode="json"),
            "final_document": ps.document.model_dump(mode="json"),
            "artifact_versions": self._versions(state, ArtifactType.DOCUMENT, ps.document.document_version,
                                                ps.document.content_hash,
                                                {ArtifactType.FINANCIAL_ESTIMATE.value: estimate_fingerprint(est)}),
            "current_stage": WorkflowStage.COMPLETED.value,
            "workflow_status": WorkflowStatus.COMPLETED.value,
            "pending_questions": [],
            "resume_stage": None,
        }

    @guarded(WorkflowStage.APPROVAL)
    async def _request_approval(self, state: WorkflowState, config: RunnableConfig):
        """Human-in-the-loop: pause for approval of the CURRENT financial estimate."""

        est = get_estimate(state)
        tp = get_technical(state)
        req = get_requirements(state)
        assert est is not None and tp is not None and req is not None
        payload = {
            "type": "approval_required",
            "estimate_version": est.version,
            "currency": est.currency,
            "total_cost": str(est.total_cost),
            "total_hours": str(est.total_hours),
            "estimated_duration": est.estimated_duration,
        }
        # Pause. Nothing above this line has side effects (the node re-runs on resume).
        response: dict[str, Any] = interrupt(payload)

        kind = response.get("kind")
        if kind == "message":
            return {"incoming_message": response.get("text", ""), "workflow_status": WorkflowStatus.RUNNING.value}
        if kind == "cancel":
            await self._say(state, "Workflow cancelled. History and artifacts are preserved.", "status")
            return {"workflow_status": WorkflowStatus.CANCELLED.value,
                    "approval_status": ApprovalStatus.CANCELLED.value}
        if kind != "approval":
            return {"errors": [f"Unsupported response at approval stage: {kind}"]}

        decision = ApprovalDecision(response["decision"])
        if int(response.get("estimate_version", -1)) != est.version:
            # Stale decision (estimate changed in between): never apply it.
            return {"errors": [
                f"Decision referenced estimate v{response.get('estimate_version')} but current is v{est.version}"]}

        record = ApprovalRecord(
            decision=decision, status=DECISION_TO_STATUS[decision], estimate_version=est.version,
            estimate_fingerprint=estimate_fingerprint(est), technical_version=tp.version,
            technical_fingerprint=technical_fingerprint(tp), requirements_fingerprint=requirements_fingerprint(req),
            user_id=str(response.get("user_id", "unknown")), feedback=response.get("feedback"),
        )
        await self._proposal_repository.save_approval(state["proposal_id"], record)
        fs = dict(state["financial_estimation_state"] or {})
        out = dict(fs["output"])
        out["approval_status"] = record.status.value
        out["approval_feedback"] = record.feedback
        fs["output"] = out
        update: dict[str, Any] = {
            "approval_record": record.model_dump(mode="json"),
            "approval_status": record.status.value,
            "financial_estimate_state": fs,
            "current_stage": WorkflowStage.APPROVAL.value,
        }
        if decision == ApprovalDecision.APPROVE:
            await self._say(state, f"Estimación v{est.version} aprobada. Generando el documento de la propuesta…", "status")
            update["workflow_status"] = WorkflowStatus.RUNNING.value
        elif decision == ApprovalDecision.REQUEST_CHANGES:
            await self._say(state, "Cambios solicitados. Actualizando estimación según feedback", "status")
            update.update(workflow_status=WorkflowStatus.RUNNING.value, user_feedback=record.feedback or "")
        elif decision == ApprovalDecision.REJECT:
            q = "La estimación fue rechazada. Describe qué debe cambiar (alcance, esfuerzo, supuestos) o selecciona Reanudar para volver a estimar."
            await self._say(state, q, "clarification")
            update.update(workflow_status=WorkflowStatus.REJECTED.value, pending_questions=[q],
                          resume_stage=N.FINANCIAL)
        else:
            await self._say(state, "Workflow cancelled. History and artifacts are preserved.", "status")
            update["workflow_status"] = WorkflowStatus.CANCELLED.value
        return update

    def _build(self) -> CompiledStateGraph:
        self._builder.add_node(N.INITIALIZE, self._initialize_proposal)
        self._builder.add_node(N.REQUIREMENTS, self._requirements_agent_node)
        self._builder.add_node(N.VALIDATION, self._requirements_validation)
        self._builder.add_node(N.ARCHITECT, self._tech_architect_agent_node)
        self._builder.add_node(N.FINANCIAL, self._financial_estimator_agent_node)
        self._builder.add_node(N.PRESENTATION, self._document_generator_agent_node)
        self._builder.add_node(N.APPROVAL, self._request_approval)
        self._builder.add_node(N.AWAITING_USER, self._awaiting_user_input)

        self._builder.add_edge(START, N.INITIALIZE)
        self._builder.add_conditional_edges(
            N.INITIALIZE, route_after_ingest, [N.REQUIREMENTS, N.VALIDATION, N.AWAITING_USER]
        )
        self._builder.add_edge(N.REQUIREMENTS, N.VALIDATION)
        self._builder.add_conditional_edges(N.VALIDATION, route_after_validation, READY_TARGETS)
        self._builder.add_conditional_edges(N.ARCHITECT, route_after_technical, READY_TARGETS)
        self._builder.add_conditional_edges(N.FINANCIAL, route_after_financial, [*READY_TARGETS, N.INITIALIZE])
        self._builder.add_conditional_edges(N.APPROVAL, route_after_approval, [*READY_TARGETS, N.INITIALIZE])

        self._builder.add_conditional_edges(
            N.AWAITING_USER, route_after_await, [N.INITIALIZE, N.VALIDATION, *READY_TARGETS]
        )
        self._builder.add_edge(N.PRESENTATION, END)

        return self._builder.compile(checkpointer=InMemorySaver(serde=serde), name="techdoc-workflow")

    def _get_config(self, user_id, session_id) -> dict[str, Any]:
        return {
            "callbacks": self._callbacks,
            "metadata": {
                "langfuse_user_id": user_id,
                "langfuse_session_id": session_id,
                "langfuse_tags": [
                    f"environment:{os.getenv('ENVIRONMENT',"dev")}",
                    "framework:langgraph",
                    f"owner:{self._app_settings.owner}",
                    f"application:{self._app_settings.name}",
                    f"component:{self._app_settings.component}"
                ]
            },
            "configurable": {
                "thread_id": session_id
            }
        }

    async def snapshot(self, thread_id: str) -> WorkflowSnapshot:
        state = await self._graph.aget_state(self._get_config(thread_id, thread_id))
        pending = [i.value for task in state.tasks for i in task.interrupts]
        return WorkflowSnapshot(thread_id, dict(state.values), pending[0] if pending else None)

    def invoke(self, initial_input: dict | Command[Any], session_id: str) -> WorkflowState:
        return self._graph.invoke(
            input=initial_input,
            config=self._get_config(session_id, session_id),
        )

    async def resume(self, thread_id: str, response: UserResponse | dict[str, Any]) -> WorkflowSnapshot:
        """Answer the pending interrupt (requirements questions or financial approval)."""
        payload = response.model_dump(mode="json", exclude_none=True) if isinstance(response,
                                                                                    UserResponse) else response
        await self._graph.ainvoke(Command(resume=payload), self._get_config(thread_id, thread_id))
        return await self.snapshot(thread_id)

    async def start(self, thread_id: str, user_request: str) -> WorkflowSnapshot:
        await self._graph.ainvoke(
            input={
                "proposal_id": thread_id,
                "user_request": user_request,
            },
            config=self._get_config(thread_id, thread_id))
        return await self.snapshot(thread_id)

    async def request_revision(
            self, thread_id: str, changes: str, *, changed_by: str = "user", reason: str | None = None
    ) -> WorkflowSnapshot:
        """Change requirements at any time: mid-flight (paused) or after completion."""
        current = await self.snapshot(thread_id)
        if current.waiting_for_user:
            return await self.resume(
                thread_id,
                UserResponse(
                    action=UserAction.CHANGE_REQUIREMENTS,
                    changes=changes,
                    changed_by=changed_by,
                    reason=reason
                ),
            )
        pending = PendingInput(kind="change", text=changes, changed_by=changed_by, reason=reason)
        await self._graph.ainvoke({"pending_input": pending}, self._get_config(thread_id, thread_id))
        return await self.snapshot(thread_id)

    def get_compiled_state_graph(self) -> CompiledStateGraph:
        return self._graph

    def draw_workflow(self):
        self._graph.get_graph().draw_mermaid_png(output_file_path="techdoc_workflow.png")