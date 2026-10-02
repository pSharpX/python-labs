from typing import List, Optional, Literal

from src.catalog.database import SessionFactory
from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.domain.segmentation_criterion import SegmentationCriterionDTO
from src.catalog.infrastructure.product_service_mapper import ProductServiceMapper
from src.catalog.infrastructure.segmentation_criterion_mapper import SegmentationCriterionMapper
from src.catalog.repositories.product_service_repository import ProductServiceRepository
from src.catalog.repositories.segmentation_criterion_repository import SegmentationCriterionRepository


SEGMENT_CODE = Literal["SMB", "CORPORATE"]

class CatalogService:
    def __init__(self):
        self.session = SessionFactory()
        self.product_repository = ProductServiceRepository(self.session)
        self.segmentation_repository = SegmentationCriterionRepository(self.session)

    def get_all_criteria(self) -> List[SegmentationCriterionDTO]:
        models = self.segmentation_repository.get_all()
        return [SegmentationCriterionMapper.to_dto(model) for model in models]

    def fetch_product_by_code(self, code: str) -> Optional[ProductServiceDTO]:
        model = self.product_repository.get_by_code(code)
        if not model:
            return None
        return ProductServiceMapper.to_dto(model)

    def fetch_catalog_for_segment(self, segment: SEGMENT_CODE) -> List[ProductServiceDTO]:
        models = self.product_repository.get_all_by_segment(segment)
        return [ProductServiceMapper.to_dto(m) for m in models]