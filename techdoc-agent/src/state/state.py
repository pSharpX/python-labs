from src.state.requirements import RequirementsState


class WorkflowState(RequirementsState):
    technical_document: str
    financial_document: str
