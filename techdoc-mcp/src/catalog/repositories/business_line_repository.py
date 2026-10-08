from typing import Sequence, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from src.catalog.models.business_line import BusinessLineModel


class BusinessLineRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> Sequence[BusinessLineModel]:
        """Recupera todas las líneas de negocio registradas."""
        stmt = (
            select(BusinessLineModel)
            .options(selectinload(BusinessLineModel.families))
            .order_by(BusinessLineModel.id)
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_code(self, code: int) -> Optional[BusinessLineModel]:
        """Busca una línea de negocio por su código único."""
        stmt = select(BusinessLineModel).where(BusinessLineModel.code == code)
        return self.session.execute(stmt).scalar_one_or_none()

    def search_by_name_or_keyword(self, keyword: str) -> Sequence[BusinessLineModel]:
        """Busca líneas de negocio coincidentes por nombre o palabras clave en familias."""
        stmt = select(BusinessLineModel).where(
            (BusinessLineModel.name.ilike(f"%{keyword}%")) |
            (BusinessLineModel.main_families.ilike(f"%{keyword}%"))
        )
        return self.session.execute(stmt).scalars().all()