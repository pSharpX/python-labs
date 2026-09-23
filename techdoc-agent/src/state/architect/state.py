from langchain.agents import AgentState

from src.state import Requirements


class TechArchitectAgentState(AgentState):
    requirements: Requirements
    technical_document: str