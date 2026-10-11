"""Artifact versioning, fingerprints and dependency-aware staleness.

Dependency chain::

    requirements ──► technical_proposal ──► financial_estimate ──► approval ──► document

Each downstream artifact records the fingerprint of the upstream artifact it was
built from. An artifact is *current* only while that fingerprint still matches.
Approval is bound to an exact estimate version **and** fingerprint, so any change to
scope, architecture, effort or price requires a fresh approval before a new approved
document can be issued (post-approval revision policy).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.shared import ApprovalStatus
from src.shared.enums import ArtifactType, TechnicalStatus, EstimateStatus
from src.shared.models import RequirementsSpecification, TechnicalProposal, ApprovalRecord, DocumentMetadata, \
    FinancialEstimate
from src.repositories.proposal_repository import ProposalRepository, StoredArtifact
from src.utils.hashing import fingerprint, utcnow


def requirements_fingerprint(spec: RequirementsSpecification) -> str:
    return fingerprint(spec, exclude=RequirementsSpecification.FINGERPRINT_EXCLUDE)


def technical_fingerprint(tp: TechnicalProposal) -> str:
    return fingerprint(tp, exclude=TechnicalProposal.FINGERPRINT_EXCLUDE)


def estimate_fingerprint(est: FinancialEstimate) -> str:
    return fingerprint(est, exclude=FinancialEstimate.FINGERPRINT_EXCLUDE)


def technical_is_current(req_fp: str | None, tp: TechnicalProposal | None) -> bool:
    return (
        tp is not None
        and req_fp is not None
        and tp.based_on_requirements_fingerprint == req_fp
        and tp.status == TechnicalStatus.READY
    )


def estimate_is_current(tp: TechnicalProposal | None, est: FinancialEstimate | None) -> bool:
    return (
        tp is not None
        and est is not None
        and est.based_on_technical_fingerprint == technical_fingerprint(tp)
        and est.status == EstimateStatus.READY_FOR_APPROVAL
    )


def approval_for_estimate(est: FinancialEstimate | None, approval: ApprovalRecord | None) -> ApprovalStatus:
    """Approval status that applies to *this exact* estimate version."""
    if est is None:
        return ApprovalStatus.NOT_REQUESTED
    if approval is None or approval.estimate_version != est.version or approval.estimate_fingerprint != estimate_fingerprint(est):
        return ApprovalStatus.PENDING if est.status == EstimateStatus.READY_FOR_APPROVAL else ApprovalStatus.NOT_REQUESTED
    return approval.status


def approval_is_valid(
    req: RequirementsSpecification | None,
    tp: TechnicalProposal | None,
    est: FinancialEstimate | None,
    approval: ApprovalRecord | None,
) -> bool:
    if req is None or tp is None or est is None or approval is None:
        return False
    req_fp = requirements_fingerprint(req)
    return (
        technical_is_current(req_fp, tp)
        and estimate_is_current(tp, est)
        and approval_for_estimate(est, approval) == ApprovalStatus.APPROVED
        and approval.technical_version == tp.version
        and approval.technical_fingerprint == technical_fingerprint(tp)
        and approval.requirements_fingerprint == req_fp
    )


def document_is_current(doc: DocumentMetadata | None, est: FinancialEstimate | None) -> bool:
    return (
        doc is not None
        and est is not None
        and doc.estimate_version == est.version
        and doc.estimate_fingerprint == estimate_fingerprint(est)
    )


def stale_artifacts(
    req: RequirementsSpecification | None,
    tp: TechnicalProposal | None,
    est: FinancialEstimate | None,
    approval: ApprovalRecord | None,
    doc: DocumentMetadata | None,
) -> list[str]:
    """Human-readable list of artifacts that need (re)generation or (re)approval."""
    stale: list[str] = []
    req_fp = requirements_fingerprint(req) if req else None
    if tp is not None and not technical_is_current(req_fp, tp):
        stale.append(ArtifactType.TECHNICAL_PROPOSAL.value)
    if est is not None and not estimate_is_current(tp, est):
        stale.append(ArtifactType.FINANCIAL_ESTIMATE.value)
    if est is not None and approval is not None and approval_for_estimate(est, approval) != ApprovalStatus.APPROVED:
        if approval.status == ApprovalStatus.APPROVED:
            stale.append("approval")
    if doc is not None and not document_is_current(doc, est):
        stale.append(ArtifactType.DOCUMENT.value)
    return stale


class VersionService:
    def __init__(self, repo: ProposalRepository) -> None:
        self._repo = repo

    async def next_version(self, proposal_id: str, artifact_type: ArtifactType) -> int:
        return await self._repo.next_version(proposal_id, artifact_type)

    async def record(
        self,
        proposal_id: str,
        artifact_type: ArtifactType,
        model: BaseModel,
        fp: str,
        based_on: dict[str, str] | None = None,
    ) -> None:
        payload: dict[str, Any] = model.model_dump(mode="json")
        await self._repo.save_artifact(
            StoredArtifact(
                proposal_id=proposal_id,
                artifact_type=artifact_type,
                version=int(payload.get("version", 1)),
                fingerprint=fp,
                based_on=based_on or {},
                payload=payload,
                created_at=utcnow(),
            )
        )
