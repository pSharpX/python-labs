from typing import Optional, List, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.catalog.models.hourly_rate import HourlyRateModel


class HourlyRateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, role_code: str) -> Optional[HourlyRateModel]:
        return self.session.query(HourlyRateModel).filter(HourlyRateModel.role_code == role_code).first()

    def get_by_role_codes(self, role_codes: List[str]) -> Sequence[HourlyRateModel]:
        """Obtiene la lista de tarifas/perfiles correspondientes a los códigos de rol especificados."""
        if not role_codes:
            return []
        stmt = select(HourlyRateModel).where(HourlyRateModel.role_code.in_(role_codes))
        return self.session.execute(stmt).scalars().all()

    def get_all(self) -> List[HourlyRateModel]:
        return self.session.query(HourlyRateModel).all()

    def get_by_category(self, category: str) -> List[HourlyRateModel]:
        return self.session.query(HourlyRateModel).filter(HourlyRateModel.category == category).all()