from pydantic import BaseModel, Field

from src.shared.models import ChatTurn, RequirementsSpecification


class RequirementsAgentState(BaseModel):
    proposal_id: str
    conversation: list[ChatTurn] = Field(default_factory=list, description="Analyst's own isolated dialogue history")
    latest_user_message: str | None = None
    spec: RequirementsSpecification | None = None
    fingerprint: str | None = None