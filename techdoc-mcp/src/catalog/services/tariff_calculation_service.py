from decimal import Decimal
from typing import Optional, Literal

from src.catalog.database import SessionFactory
from src.catalog.domain.cost_calculation import CostCalculationDTO
from src.catalog.repositories.hourly_rate_repository import HourlyRateRepository
from src.catalog.repositories.surcharge_repository import SurchargeRepository


SEGMENT_CODE = Literal["SMB", "CORPORATE"]

class TariffCalculationService:
    def __init__(self):
        self.session = SessionFactory()
        self.hourly_rate_repo = HourlyRateRepository(self.session)
        self.surcharge_repo = SurchargeRepository(self.session)

    def calculate_service_cost(
            self,
            role_code: str,
            segment: SEGMENT_CODE,  # 'SMB' or 'Corporate'
            hours: float,
            surcharge_code: Optional[str] = None
    ) -> CostCalculationDTO:

        # 1. Fetch role
        role_model = self.hourly_rate_repo.get_by_code(role_code)
        if not role_model:
            raise ValueError(f"Role code '{role_code}' not found.")

        # 2. Determine base rate according to segment
        segment_upper = segment.strip().upper()
        if segment_upper == 'SMB':
            base_rate = role_model.smb_rate
        elif segment_upper == 'CORPORATE':
            base_rate = role_model.corporate_rate
        else:
            raise ValueError("Segment must be either 'SMB' or 'Corporate'.")

        # 3. Apply surcharge factor if present
        factor = Decimal('1.0')
        if surcharge_code:
            surcharge_model = self.surcharge_repo.get_by_code(surcharge_code)
            if surcharge_model:
                factor = surcharge_model.factor

        # 4. Compute calculation
        hours_dec = Decimal(str(hours))
        total_cost = base_rate * factor * hours_dec

        return CostCalculationDTO(
            role_code=role_model.role_code,
            position=role_model.position,
            segment=segment_upper,
            base_rate=base_rate,
            surcharge_code=surcharge_code,
            surcharge_factor=factor,
            hours=hours_dec,
            total_cost=total_cost
        )