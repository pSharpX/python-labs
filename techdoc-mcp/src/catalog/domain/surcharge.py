from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class SurchargeDTO:
    code: str
    condition: str
    factor: Decimal
    rule: Optional[str]