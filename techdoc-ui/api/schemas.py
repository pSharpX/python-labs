"""Client-side views of backend responses (tolerant to additional fields)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class _Loose(BaseModel):
    model_config = ConfigDict(extra="ignore")


class EstimateHeadline(_Loose):
    version: int
    currency: str
    total_cost: Decimal
    total_hours: Decimal
    estimated_duration: str = ""
    status: str
    approval_status: str


class ArtifactVersions(_Loose):
    requirements: int | None = None
    technical_proposal: int | None = None
    financial_estimate: int | None = None
    document: int | None = None


class ProposalSummary(_Loose):
    proposal_id: str
    title: str
    customer_name: str = ""
    workflow_status: str
    current_stage: str
    run_state: str
    last_error: str | None = None
    pending_questions: list[str] = []
    awaiting: str | None = None
    approval_status: str
    revision_number: int = 0
    artifact_versions: ArtifactVersions = ArtifactVersions()
    stale_artifacts: list[str] = []
    estimate: EstimateHeadline | None = None
    has_document: bool = False
    recent_errors: list[str] = []
    updated_at: datetime

    @property
    def is_running(self) -> bool:
        return self.run_state == "running"


class ProposalListItem(_Loose):
    proposal_id: str
    title: str
    customer_name: str = ""
    workflow_status: str
    current_stage: str
    run_state: str
    updated_at: datetime


class Message(_Loose):
    role: str
    content: str
    kind: str = "chat"
    created_at: datetime


class Versions(_Loose):
    proposal_id: str
    artifacts: list[dict[str, Any]] = []
    approvals: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
