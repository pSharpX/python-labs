from typing import TypedDict, Optional


class FinancialEstimatorAgentState(TypedDict):
    technical_proposal_version: int
    #service_items: list[ServiceItem]
    #effort_breakdown: list[EffortItem]
    hourly_rate: object | None
    estimated_hours: object | None
    subtotal: object | None
    taxes: object | None
    total: object | None
    currency: str
    assumptions: list[str]
    financial_proposal: str | None
    approval_status: str
    user_feedback: str | None
    status: str
    version: int
    stale: bool

