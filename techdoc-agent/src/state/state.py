import operator
from typing import TypedDict, Optional, Annotated, Any

from src.shared.models import RequirementsSpecification, TechnicalProposal, FinancialEstimate, ApprovalRecord, \
    DocumentMetadata
from src.state.architect import TechArchitectAgentState
from src.state.financial_estimator import FinancialEstimatorAgentState
from src.state.presentation import PresentationAgentState
from src.state.requirements import RequirementsAgentState


class WorkflowState(TypedDict):
    proposal_id: str
    thread_id: str
    user_id: str
    title: str
    customer_name: str
    conversation_history: Annotated[list[dict[str, Any]], operator.add]
    incoming_message: str | None

    user_request: str

    requirements_state: Optional[RequirementsAgentState]
    technical_architecture_state: Optional[TechArchitectAgentState]
    financial_estimation_state: Optional[FinancialEstimatorAgentState]
    presentation_state: Optional[PresentationAgentState]

    current_stage: str
    workflow_status: str
    pending_questions: list[str]
    user_feedback: str | None
    approval_status: str
    approval_record: dict[str, Any] | None
    revision_number: int
    artifact_versions: dict[str, dict[str, Any]]

    final_document: dict[str, Any] | None
    resume_stage: str | None
    scope_redirected: bool
    errors: Annotated[list[str], operator.add]

def get_requirements(state: WorkflowState) -> RequirementsSpecification | None:
    rs = state.get("requirements_state") or {}
    spec = rs.get("spec")
    return RequirementsSpecification.model_validate(spec) if spec else None

def get_technical(state: WorkflowState) -> TechnicalProposal | None:
    ts = state.get("technical_architecture_state") or {}
    out = ts.get("output")
    return TechnicalProposal.model_validate(out) if out else None

def get_estimate(state: WorkflowState) -> FinancialEstimate | None:
    fs = state.get("financial_estimation_state") or {}
    out = fs.get("output")
    return FinancialEstimate.model_validate(out) if out else None

def get_approval(state: WorkflowState) -> ApprovalRecord | None:
    rec = state.get("approval_record")
    return ApprovalRecord.model_validate(rec) if rec else None

def get_document(state: WorkflowState) -> DocumentMetadata | None:
    doc = state.get("final_document")
    return DocumentMetadata.model_validate(doc) if doc else None
