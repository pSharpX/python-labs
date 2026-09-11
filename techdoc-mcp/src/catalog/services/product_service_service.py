from typing import List, Optional, Literal

from src.catalog.database import SessionFactory
from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.infrastructure.product_service_mapper import ProductServiceMapper
from src.catalog.repositories.product_service_repository import ProductServiceRepository


SEGMENT_CODE = Literal["SMB", "CORPORATE"]

class CatalogService:
    def __init__(self):
        self.session = SessionFactory()
        self.repository = ProductServiceRepository(self.session)

    def fetch_product_by_code(self, code: str) -> Optional[ProductServiceDTO]:
        model = self.repository.get_by_code(code)
        if not model:
            return None
        return ProductServiceMapper.to_dto(model)

    def fetch_catalog_for_segment(self, segment: SEGMENT_CODE) -> List[ProductServiceDTO]:
        models = self.repository.get_all_by_segment(segment)
        return [ProductServiceMapper.to_dto(m) for m in models]