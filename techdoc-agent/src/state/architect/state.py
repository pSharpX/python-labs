from langchain.agents import AgentState

from state import Requirements


class TechArchitectState(AgentState):
    requirements: Requirements
    technical_document: str