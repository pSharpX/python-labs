"""Public API request/response models (no internal graph state, no filesystem paths)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

from src.shared import ApprovalDecision, ApprovalStatus, WorkflowStatus, WorkflowStage
from src.shared.models import ApprovalRecord


class ErrorBody(BaseModel):
    code: str
    message: str
    trace_id: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class ProposalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    customer_name: str = Field(default="", max_length=200)
    message: str = Field(min_length=1, max_length=20000, description="Initial description of the business need")


class MessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20000)


class ApprovalRequest(BaseModel):
    decision: ApprovalDecision
    estimate_version: int = Field(ge=1, description="The estimate version being decided on (prevents stale approvals)")
    feedback: str | None = Field(default=None, max_length=8000)


class ResumeRequest(BaseModel):
    action: Literal["retry", "cancel"] = "retry"


class EstimateHeadline(BaseModel):
    version: int
    currency: str
    total_cost: Decimal
    total_hours: Decimal
    estimated_duration: str
    status: str
    approval_status: ApprovalStatus


class ArtifactVersionsSummary(BaseModel):
    requirements: int | None = None
    technical_proposal: int | None = None
    financial_estimate: int | None = None
    document: int | None = None


class ProposalSummary(BaseModel):
    proposal_id: str
    title: str
    customer_name: str
    workflow_status: WorkflowStatus
    current_stage: WorkflowStage
    run_state: str
    last_error: str | None
    pending_questions: list[str]
    awaiting: Literal["clarification", "approval"] | None
    approval_status: ApprovalStatus
    revision_number: int
    artifact_versions: ArtifactVersionsSummary
    stale_artifacts: list[str]
    estimate: EstimateHeadline | None
    has_document: bool
    recent_errors: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ProposalListItem(BaseModel):
    proposal_id: str
    title: str
    customer_name: str
    workflow_status: WorkflowStatus
    current_stage: WorkflowStage
    run_state: str
    updated_at: datetime


class MessageOut(BaseModel):
    role: str
    content: str
    kind: str
    created_at: datetime


class ArtifactVersionOut(BaseModel):
    artifact_type: str
    version: int
    fingerprint: str
    based_on: dict[str, str]
    created_at: datetime
    status: str | None = None


class DocumentInfo(BaseModel):
    document_version: int
    filename: str
    created_at: datetime
    approval_status: ApprovalStatus
    content_hash: str
    requirements_version: int
    technical_version: int
    estimate_version: int
    download_url: str


class VersionsResponse(BaseModel):
    proposal_id: str
    artifacts: list[ArtifactVersionOut]
    approvals: list[ApprovalRecord]
    documents: list[DocumentInfo]


class HealthResponse(BaseModel):
    status: str
    version: str
    mcp_available: bool
    mcp_detail: str | None
