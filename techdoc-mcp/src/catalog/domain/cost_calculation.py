from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class CostCalculationDTO:
    role_code: str
    position: str
    segment: str
    base_rate: Decimal
    surcharge_code: Optional[str]
    surcharge_factor: Decimal
    hours: Decimal
    total_cost: Decimal