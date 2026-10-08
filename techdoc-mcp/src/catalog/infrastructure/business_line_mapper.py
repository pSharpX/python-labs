from typing import List, Optional

from src.catalog.infrastructure.family_mapper import FamilyMapper
from src.catalog.domain.business_line import BusinessLineDTO
from src.catalog.models.business_line import BusinessLineModel


class BusinessLineMapper:
    @staticmethod
    def _parse_families(families_text: Optional[str]) -> List[str]:
        """Convierte la cadena de familias en una lista limpia de strings."""
        if not families_text:
            return []
        return [f.strip() for f in families_text.split(",") if f.strip()]

    @classmethod
    def to_dto(cls, model: BusinessLineModel) -> BusinessLineDTO:
        """Convierte una entidad BusinessLineModel a BusinessLineDTO."""
        return BusinessLineDTO(
            id=model.id,
            code=model.code,
            name=model.name,
            families=[
                FamilyMapper.to_dto(family)
                for family in model.families
            ],
        )