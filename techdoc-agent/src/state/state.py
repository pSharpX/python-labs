from typing import Annotated

from langchain.agents import AgentState

from src.shared import merge_status
from .models import Requirements


class WorkflowState(AgentState):
    status: Annotated[str, merge_status]
    requirements: Requirements
    technical_document: str
    financial_document: str
