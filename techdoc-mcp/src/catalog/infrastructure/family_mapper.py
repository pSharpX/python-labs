from src.catalog.domain.family import FamilyDTO
from src.catalog.models.family import FamilyModel


class FamilyMapper:

    @staticmethod
    def to_dto(model: FamilyModel) -> FamilyDTO:
        return FamilyDTO(
            id=model.id,
            name=model.name,
        )