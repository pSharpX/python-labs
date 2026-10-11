from pydantic import BaseModel

from src.shared import NarrativeDraft, DocumentMetadata
from src.shared.models import ApprovalRecord, RequirementsSpecification, TechnicalProposal, FinancialEstimate


class PresentationAgentState(BaseModel):
    proposal_id: str
    title: str
    customer_name: str

    requirements: RequirementsSpecification
    technical: TechnicalProposal
    estimate: FinancialEstimate

    approval: ApprovalRecord | None
    narrative: NarrativeDraft | None = None
    document: DocumentMetadata | None = None

