from typing import Optional

from sqlalchemy.orm import Session

from src.catalog.models.surcharge import SurchargeModel


class SurchargeRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, code: str) -> Optional[SurchargeModel]:
        return self.session.query(SurchargeModel).filter(SurchargeModel.code == code).first()