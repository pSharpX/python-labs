from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Optional

from src.catalog.models.family import FamilyModel
from src.catalog.models.product_service import ProductServiceModel


class ProductServiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, code: str) -> Optional[ProductServiceModel]:
        stmt = (
            select(ProductServiceModel)
            .options(
                joinedload(ProductServiceModel.family)
                .joinedload(FamilyModel.business_line)
            )
            .where(ProductServiceModel.code == code)
        )
        return self.session.scalar(stmt)

    def get_all_by_segment(self, segment: str) -> List[ProductServiceModel]:
        stmt = select(ProductServiceModel).options(
            joinedload(ProductServiceModel.family)
            .joinedload(FamilyModel.business_line)
        )
        if segment.upper() == "SMB":
            stmt = stmt.where(ProductServiceModel.smb_applicable == True)
        elif segment.upper() == "CORPORATE":
            stmt = stmt.where(ProductServiceModel.corp_applicable == True)

        return list(self.session.scalars(stmt).unique().all())