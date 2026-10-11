from pydantic import BaseModel

from src.shared.models import FinancialEstimate, TechnicalProposal


class FinancialEstimatorAgentState(BaseModel):
    proposal_id: str
    technical: TechnicalProposal
    technical_fingerprint: str
    feedback: str | None = None
    previous_estimate_version: int | None = None
    output: FinancialEstimate | None = None
    fingerprint: str | None = None
    scope_change_detected: bool = False

