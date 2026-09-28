from decimal import Decimal

from pydantic import BaseModel, Field


class FinancialEstimatorOutputSchema(BaseModel):
    #service_items: list[ServiceItem] = Field(default_factory=list)
    #effort_breakdown: list[EffortItem] = Field(default_factory=list)
    hourly_rate: Decimal | None = None
    estimated_hours: Decimal | None = None
    subtotal: Decimal | None = None
    taxes: Decimal | None = None
    total: Decimal | None = None
    currency: str = "USD"
    assumptions: list[str] = Field(default_factory=list)
    financial_proposal: str