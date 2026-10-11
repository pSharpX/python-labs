from pydantic import BaseModel

from src.shared.models import RequirementsSpecification, TechnicalProposal


class TechArchitectAgentState(BaseModel):
    proposal_id: str
    requirements: RequirementsSpecification
    requirements_fingerprint: str
    feedback: str | None = None
    #classification_trace: list[ClassificationTrace] = Field(default_factory=list)
    #documentation_findings: list[DocumentationFinding] = Field(default_factory=list)
    documentation_status: str = ""
    output: TechnicalProposal | None = None
    fingerprint: str | None = None
