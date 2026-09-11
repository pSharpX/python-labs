from src.catalog.domain.specialty import SpecialtyDTO
from src.ccatalog.models.specialty import SpecialtyModel


class SpecialtyMapper:
    @staticmethod
    def to_dto(model: SpecialtyModel) -> SpecialtyDTO:
        return SpecialtyDTO(
            code=model.code,
            name=model.name,
            code_example=model.code_example
        )

