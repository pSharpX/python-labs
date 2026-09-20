from src.state.requirements import TechDocReqScoutState


class TechDocBuilderState(TechDocReqScoutState):
    technical_document: str
    financial_document: str
