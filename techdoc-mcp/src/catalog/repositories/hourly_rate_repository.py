from typing import Optional, List

from sqlalchemy.orm import Session

from src.catalog.models.hourly_rate import HourlyRateModel


class HourlyRateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, role_code: str) -> Optional[HourlyRateModel]:
        return self.session.query(HourlyRateModel).filter(HourlyRateModel.role_code == role_code).first()

    def get_all(self) -> List[HourlyRateModel]:
        return self.session.query(HourlyRateModel).all()

    def get_by_category(self, category: str) -> List[HourlyRateModel]:
        return self.session.query(HourlyRateModel).filter(HourlyRateModel.category == category).all()