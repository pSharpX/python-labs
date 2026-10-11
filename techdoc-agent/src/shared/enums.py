from enum import Enum, StrEnum


class WorkflowStage(StrEnum):
    INITIALIZE = "initialize"
    REQUIREMENTS = "requirements"
    TECHNICAL_ARCHITECTURE = "technical_architecture"
    FINANCIAL_ESTIMATION = "financial_estimation"
    DOCUMENT_GENERATION = "document_generation"
    AWAIT_USER_INPUT = "await_user_input"
    APPROVAL = "approval"
    COMPLETED = "completed"

class UserAction(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"  # change the financial estimate
    CHANGE_REQUIREMENTS = "change_requirements"  # change the customer requirements
    PROVIDE_INFORMATION = "provide_information"  # answer the analyst's questions

class RequirementStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    AWAITING_USER = "awaiting_user"
    READY = "ready"
    INVALID = "invalid"

class TechnicalStatus(StrEnum):
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    FAILED = "failed"

class EstimateStatus(StrEnum):
    READY_FOR_APPROVAL = "ready_for_approval"
    INVALID = "invalid"

class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    CANCEL = "cancel"

class ApprovalStatus(StrEnum):
    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    CANCELLED = "cancelled"

DECISION_TO_STATUS: dict[ApprovalDecision, ApprovalStatus] = {
    ApprovalDecision.APPROVE: ApprovalStatus.APPROVED,
    ApprovalDecision.REJECT: ApprovalStatus.REJECTED,
    ApprovalDecision.REQUEST_CHANGES: ApprovalStatus.CHANGES_REQUESTED,
    ApprovalDecision.CANCEL: ApprovalStatus.CANCELLED,
}

class ArtifactType(StrEnum):
    REQUIREMENTS = "requirements"
    TECHNICAL_PROPOSAL = "technical_proposal"
    FINANCIAL_ESTIMATE = "financial_estimate"
    DOCUMENT = "document"

class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"