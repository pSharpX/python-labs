from typing import TypedDict, Optional, List

from src.state.architect import TechArchitectAgentState
from src.state.financial_estimator import FinancialEstimatorAgentState
from src.state.requirements import RequirementsAgentState
from src.shared import ProposalRevision


class WorkflowState(TypedDict):
    proposal_id: str
    user_request: str
    revision_request: str | None
    revision_reason: str | None

    requirements: Optional[RequirementsAgentState]
    technical_architecture: Optional[TechArchitectAgentState]
    financial_estimation: Optional[FinancialEstimatorAgentState]

    current_stage: str
    status: str
    revision: int
    revision_history: List[ProposalRevision]
    errors: List[str]
