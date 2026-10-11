from datetime import datetime

from pydantic import BaseModel, Field

from src.shared import WorkflowStatus
from src.shared import ApprovalStatus, WorkflowStage
from src.utils.hashing import utcnow


class RunState:
    IDLE = "idle"
    RUNNING = "running"
    FAILED = "failed"

class ProposalRecord(BaseModel):
    proposal_id: str
    owner_id: str
    title: str
    customer_name: str = ""
    thread_id: str
    workflow_status: WorkflowStatus = WorkflowStatus.RUNNING
    current_stage: WorkflowStage = WorkflowStage.REQUIREMENTS
    run_state: str = RunState.IDLE
    last_error: str | None = None
    pending_questions: list[str] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUESTED
    revision_number: int = 0
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

