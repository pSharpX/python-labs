from __future__ import annotations

from langgraph.constants import END

from src.services.version_service import technical_is_current, requirements_fingerprint, technical_fingerprint, \
    approval_for_estimate, document_is_current
from src.shared import WorkflowStatus
from src.shared.enums import EstimateStatus, TechnicalStatus, RequirementStatus, ApprovalStatus
from src.state import WorkflowState
from src.state.state import get_requirements, get_technical, get_estimate, get_approval, get_document


class N:
    """Node names."""

    INITIALIZE = "initialize_proposal"
    REQUIREMENTS = "requirements_agent"
    VALIDATION = "requirements_validation"
    AWAITING_USER = "awaiting_user_input"
    ARCHITECT = "technical_architect"
    FINANCIAL = "financial_estimator"
    PRESENTATION = "presentation_agent"
    APPROVAL = "request_approval"
    COMPLETE = "complete"
    USER_CHANGES = "user_changes_requirements"
    FAILED = "failed"


READY_TARGETS = [N.ARCHITECT, N.FINANCIAL, N.APPROVAL, N.PRESENTATION, N.AWAITING_USER, END]
RESUMABLE_STAGES = {N.VALIDATION, N.ARCHITECT, N.FINANCIAL, N.APPROVAL, N.PRESENTATION}

def next_stage_for_ready(state: WorkflowState) -> str:
    """Given ready requirements, return the first stage whose output is missing or stale."""
    req = get_requirements(state)
    if req is None or req.status != RequirementStatus.READY:
        return N.AWAITING_USER
    tp = get_technical(state)
    if not technical_is_current(requirements_fingerprint(req), tp):
        return N.ARCHITECT
    assert tp is not None
    est = get_estimate(state)
    if est is None or est.based_on_technical_fingerprint != technical_fingerprint(tp) or est.status == EstimateStatus.INVALID:
        return N.FINANCIAL
    status = approval_for_estimate(est, get_approval(state))
    if status == ApprovalStatus.PENDING:
        return N.APPROVAL
    if status in (ApprovalStatus.REJECTED, ApprovalStatus.CHANGES_REQUESTED):
        return N.FINANCIAL  # revise the estimate using the recorded feedback
    if status == ApprovalStatus.APPROVED:
        return END if document_is_current(get_document(state), est) else N.PRESENTATION
    return N.AWAITING_USER

def route_after_ingest(state: WorkflowState) -> str:
    if state.get("incoming_message"):
        return N.REQUIREMENTS
    if get_requirements(state) is not None:
        return N.VALIDATION
    return N.AWAITING_USER

def route_after_validation(state: WorkflowState) -> str:
    req = get_requirements(state)
    if req is None or req.status != RequirementStatus.READY:
        return N.AWAITING_USER
    return next_stage_for_ready(state)

def route_after_technical(state: WorkflowState) -> str:
    tp = get_technical(state)
    if tp is None or tp.status != TechnicalStatus.READY:
        return N.AWAITING_USER
    return next_stage_for_ready(state)

def route_after_financial(state: WorkflowState) -> str:
    if state.get("incoming_message"):  # feedback changed scope → back to requirements
        return N.INITIALIZE
    est = get_estimate(state)
    if est is None or est.status == EstimateStatus.INVALID:
        return N.AWAITING_USER
    return next_stage_for_ready(state)

def route_after_approval(state: WorkflowState) -> str:
    if state.get("incoming_message"):
        return N.INITIALIZE
    if state.get("workflow_status") == WorkflowStatus.CANCELLED:
        return END
    if state.get("workflow_status") == WorkflowStatus.REJECTED:
        return N.AWAITING_USER
    return next_stage_for_ready(state)

def route_after_await(state: WorkflowState) -> str:
    if state.get("workflow_status") == WorkflowStatus.CANCELLED:
        return END
    if state.get("incoming_message"):
        return N.INITIALIZE
    stage = state.get("resume_stage")
    if stage in RESUMABLE_STAGES:
        return stage
    return N.VALIDATION if get_requirements(state) else N.AWAITING_USER
