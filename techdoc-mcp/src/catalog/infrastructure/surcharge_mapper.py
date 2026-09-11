from src.catalog.domain.surcharge import SurchargeDTO
from src.catalog.models.surcharge import SurchargeModel


class SurchargeMapper:
    @staticmethod
    def to_dto(model: SurchargeModel) -> SurchargeDTO:
        return SurchargeDTO(
            code=model.code,
            condition=model.condition,
            factor=model.factor,
            rule=model.rule
        )