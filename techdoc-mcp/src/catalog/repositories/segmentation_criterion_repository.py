from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.catalog.models.segmentation_criterion import SegmentationCriterionModel


class SegmentationCriterionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, criterion_id: int) -> Optional[SegmentationCriterionModel]:
        """Obtiene un criterio por su ID."""
        stmt = select(SegmentationCriterionModel).where(SegmentationCriterionModel.id == criterion_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_criterion_name(self, criterion_name: str) -> Optional[SegmentationCriterionModel]:
        """Busca un criterio por su nombre exacto."""
        stmt = select(SegmentationCriterionModel).where(SegmentationCriterionModel.criterion == criterion_name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all(self) -> Sequence[SegmentationCriterionModel]:
        """Obtiene todos los criterios de segmentación."""
        stmt = select(SegmentationCriterionModel)
        return self.session.execute(stmt).scalars().all()