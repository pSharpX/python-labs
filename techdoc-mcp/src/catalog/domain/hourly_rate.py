from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class HourlyRateDTO:
    role_code: str
    category: str
    position: str
    level: Optional[str]
    smb_rate: Decimal
    corporate_rate: Decimal
    description: Optional[str]