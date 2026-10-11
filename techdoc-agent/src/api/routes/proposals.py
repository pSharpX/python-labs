"""Proposal endpoints (``/api/v1/proposals``)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import FileResponse, JSONResponse

from src.shared.models import RequirementsSpecification, TechnicalProposal, FinancialEstimate
from src.api.dependencies import AppContainer, get_container, get_principal, get_service
from src.api.schemas import (
    ApprovalRequest,
    ArtifactVersionOut,
    ArtifactVersionsSummary,
    DocumentInfo,
    ErrorResponse,
    EstimateHeadline,
    MessageOut,
    MessageRequest,
    ProposalCreateRequest,
    ProposalListItem,
    ProposalSummary,
    ResumeRequest,
    VersionsResponse,
)

from src.services.document_service import DocumentGenerationError
from src.services.proposal_service import NotFoundError, Principal, ProposalService

router = APIRouter(prefix="/proposals", tags=["proposals"])

ERRORS: dict[int | str, dict[str, Any]] = {
    400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse},
    409: {"model": ErrorResponse}, 422: {"model": ErrorResponse},
}
WAIT_DOC = "Block until the workflow pauses or finishes (useful for scripts/tests). Default: run in background and poll."


async def _summary(service: ProposalService, principal: Principal, proposal_id: str, base_url: str) -> ProposalSummary:
    v = await service.view(principal, proposal_id)
    rec = v.record
    awaiting = None
    if v.interrupt and rec.run_state != "running":
        awaiting = "approval" if v.interrupt.get("type") == "approval_required" else "clarification"
    est = v.estimate
    return ProposalSummary(
        proposal_id=rec.proposal_id, title=rec.title, customer_name=rec.customer_name,
        workflow_status=rec.workflow_status, current_stage=rec.current_stage, run_state=rec.run_state,
        last_error=rec.last_error, pending_questions=rec.pending_questions, awaiting=awaiting,
        approval_status=rec.approval_status, revision_number=rec.revision_number,
        artifact_versions=ArtifactVersionsSummary(
            requirements=v.requirements.version if v.requirements else None,
            technical_proposal=v.technical.version if v.technical else None,
            financial_estimate=est.version if est else None,
            document=v.document.document_version if v.document else None,
        ),
        stale_artifacts=v.stale,
        estimate=EstimateHeadline(
            version=est.version, currency=est.currency, total_cost=est.total_cost, total_hours=est.total_hours,
            estimated_duration=est.estimated_duration, status=est.status.value, approval_status=est.approval_status,
        ) if est else None,
        has_document=v.document is not None,
        recent_errors=v.errors,
        created_at=rec.created_at, updated_at=rec.updated_at,
    )


async def _idempotent(
    container: AppContainer, principal: Principal, key: str | None, scope: str
) -> dict[str, Any] | None:
    if not key:
        return None
    return await container.repository.get_idempotent(f"{scope}:{key}", principal.user_id)


async def _remember(container: AppContainer, principal: Principal, key: str | None, scope: str, body: ProposalSummary) -> None:
    if key:
        await container.repository.put_idempotent(f"{scope}:{key}", principal.user_id, body.model_dump(mode="json"))


@router.post("", response_model=ProposalSummary, status_code=status.HTTP_202_ACCEPTED, responses=ERRORS,
             summary="Create a proposal and start the workflow")
async def create_proposal(
    body: ProposalCreateRequest,
    request: Request,
    wait: bool = Query(False, description=WAIT_DOC),
    idempotency_key: str | None = Header(default=None, max_length=128),
    principal: Principal = Depends(get_principal),
    service: ProposalService = Depends(get_service),
    container: AppContainer = Depends(get_container),
) -> Any:
    if (cached := await _idempotent(container, principal, idempotency_key, "create")) is not None:
        return JSONResponse(cached, status_code=status.HTTP_202_ACCEPTED)
    rec = await service.create(principal, body.title, body.customer_name, body.message, wait=wait)
    summary = await _summary(service, principal, rec.proposal_id, str(request.base_url))
    await _remember(container, principal, idempotency_key, "create", summary)
    return summary


@router.get("", response_model=list[ProposalListItem], summary="List proposals visible to the caller")
async def list_proposals(
    principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service)
) -> Any:
    return [ProposalListItem(**r.model_dump()) for r in await service.list(principal)]


@router.get("/{proposal_id}", response_model=ProposalSummary, responses=ERRORS, summary="Current status and summary")
async def get_proposal(
    proposal_id: str, request: Request,
    principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service),
) -> Any:
    return await _summary(service, principal, proposal_id, str(request.base_url))


@router.post("/{proposal_id}/messages", response_model=ProposalSummary, status_code=status.HTTP_202_ACCEPTED,
             responses=ERRORS, summary="Send a chat message (answers, new information or requirement changes)")
async def post_message(
    proposal_id: str, body: MessageRequest, request: Request,
    wait: bool = Query(False, description=WAIT_DOC),
    idempotency_key: str | None = Header(default=None, max_length=128),
    principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service),
    container: AppContainer = Depends(get_container),
) -> Any:
    scope = f"msg:{proposal_id}"
    if (cached := await _idempotent(container, principal, idempotency_key, scope)) is not None:
        return JSONResponse(cached, status_code=status.HTTP_202_ACCEPTED)
    await service.send_message(principal, proposal_id, body.content, wait=wait)
    summary = await _summary(service, principal, proposal_id, str(request.base_url))
    await _remember(container, principal, idempotency_key, scope, summary)
    return summary


@router.get("/{proposal_id}/messages", response_model=list[MessageOut], responses=ERRORS, summary="Chat history")
async def get_messages(
    proposal_id: str, principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service)
) -> Any:
    return [MessageOut(**m.model_dump()) for m in await service.messages(principal, proposal_id)]


@router.get("/{proposal_id}/requirements", response_model=RequirementsSpecification, responses=ERRORS)
async def get_requirements(
    proposal_id: str, principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service)
) -> Any:
    v = await service.view(principal, proposal_id)
    if v.requirements is None:
        raise NotFoundError("Requirements have not been captured yet")
    return v.requirements


@router.get("/{proposal_id}/technical-proposal", response_model=TechnicalProposal, responses=ERRORS)
async def get_technical_proposal(
    proposal_id: str, principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service)
) -> Any:
    v = await service.view(principal, proposal_id)
    if v.technical is None:
        raise NotFoundError("No technical proposal yet")
    return v.technical


@router.get("/{proposal_id}/estimate", response_model=FinancialEstimate, responses=ERRORS)
async def get_estimate(
    proposal_id: str, principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service)
) -> Any:
    v = await service.view(principal, proposal_id)
    if v.estimate is None:
        raise NotFoundError("No financial estimate yet")
    return v.estimate


@router.post("/{proposal_id}/approval", response_model=ProposalSummary, status_code=status.HTTP_202_ACCEPTED,
             responses=ERRORS, summary="Approve, reject, request changes to, or cancel the pending estimate")
async def post_approval(
    proposal_id: str, body: ApprovalRequest, request: Request,
    wait: bool = Query(False, description=WAIT_DOC),
    idempotency_key: str | None = Header(default=None, max_length=128),
    principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service),
    container: AppContainer = Depends(get_container),
) -> Any:
    scope = f"approval:{proposal_id}"
    if (cached := await _idempotent(container, principal, idempotency_key, scope)) is not None:
        return JSONResponse(cached, status_code=status.HTTP_202_ACCEPTED)
    await service.decide(principal, proposal_id, body.decision, body.feedback, body.estimate_version, wait=wait)
    summary = await _summary(service, principal, proposal_id, str(request.base_url))
    await _remember(container, principal, idempotency_key, scope, summary)
    return summary


@router.post("/{proposal_id}/resume", response_model=ProposalSummary, status_code=status.HTTP_202_ACCEPTED,
             responses=ERRORS, summary="Retry a paused/failed stage, or cancel a paused workflow")
async def post_resume(
    proposal_id: str, request: Request, body: ResumeRequest | None = None,
    wait: bool = Query(False, description=WAIT_DOC),
    principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service),
) -> Any:
    await service.resume(principal, proposal_id, (body or ResumeRequest()).action, wait=wait)
    return await _summary(service, principal, proposal_id, str(request.base_url))


@router.get("/{proposal_id}/versions", response_model=VersionsResponse, responses=ERRORS,
            summary="Artifact versions, approval audit trail and document versions")
async def get_versions(
    proposal_id: str, principal: Principal = Depends(get_principal), service: ProposalService = Depends(get_service)
) -> Any:
    artifacts, approvals, documents = await service.versions(principal, proposal_id)
    return VersionsResponse(
        proposal_id=proposal_id,
        artifacts=[
            ArtifactVersionOut(artifact_type=a.artifact_type.value, version=a.version, fingerprint=a.fingerprint[:16],
                               based_on={k: v[:16] for k, v in a.based_on.items()}, created_at=a.created_at,
                               status=a.payload.get("status") or a.payload.get("approval_status"))
            for a in artifacts
        ],
        approvals=approvals,
        documents=[_doc_info(proposal_id, d) for d in documents],
    )


def _doc_info(proposal_id: str, d: Any) -> DocumentInfo:
    return DocumentInfo(
        document_version=d.document_version, filename=d.filename, created_at=d.created_at,
        approval_status=d.approval_status, content_hash=d.content_hash, requirements_version=d.requirements_version,
        technical_version=d.technical_version, estimate_version=d.estimate_version,
        download_url=f"/api/v1/proposals/{proposal_id}/document?version={d.document_version}",
    )


@router.get(
    "/{proposal_id}/document",
    responses={**ERRORS, 200: {"content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}}}},
    summary="Download the approved Word document (latest, or a specific version)",
)
async def download_document(
    proposal_id: str,
    version: int | None = Query(default=None, ge=1),
    principal: Principal = Depends(get_principal),
    service: ProposalService = Depends(get_service),
    container: AppContainer = Depends(get_container),
) -> FileResponse:
    meta = await service.document(principal, proposal_id, version)
    try:
        path = container.documents.resolve(meta.file_path)
    except DocumentGenerationError as exc:
        raise NotFoundError("Document unavailable") from exc
    if not path.is_file():
        raise NotFoundError("Document file is missing from storage")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=meta.filename,
        headers={"X-Content-SHA256": meta.content_hash, "Cache-Control": "no-store"},
    )
