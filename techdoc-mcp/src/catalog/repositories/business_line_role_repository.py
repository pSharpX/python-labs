from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from catalog.models.business_line_role import BusinessLineRoleModel


class BusinessLineRoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_business_line(self, business_line: str) -> Sequence[BusinessLineRoleModel]:
        """Consulta todas las asignaciones de roles asociadas a una línea de negocio."""
        stmt = select(BusinessLineRoleModel).where(
            BusinessLineRoleModel.business_line.ilike(f"%{business_line}%")
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_business_line_and_segment(
        self, business_line: str, segment: str
    ) -> Sequence[BusinessLineRoleModel]:
        """Consulta roles según la línea de negocio y el segmento objetivo."""
        stmt = select(BusinessLineRoleModel).where(
            BusinessLineRoleModel.business_line.ilike(f"%{business_line}%"),
            BusinessLineRoleModel.target_segment.ilike(f"%{segment}%")
        )
        return self.session.execute(stmt).scalars().all()

    def get_all(self) -> Sequence[BusinessLineRoleModel]:
        """Obtiene todas las parametrizaciones de líneas de negocio y roles."""
        stmt = select(BusinessLineRoleModel)
        return self.session.execute(stmt).scalars().all()