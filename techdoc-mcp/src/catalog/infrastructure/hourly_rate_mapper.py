from src.catalog.domain.hourly_rate import HourlyRateDTO
from src.catalog.models.hourly_rate import HourlyRateModel


class HourlyRateMapper:
    @staticmethod
    def to_dto(model: HourlyRateModel) -> HourlyRateDTO:
        return HourlyRateDTO(
            role_code=model.role_code,
            category=model.category,
            position=model.position,
            level=model.level,
            smb_rate=model.smb_rate,
            corporate_rate=model.corporate_rate,
            description=model.description
        )

    @staticmethod
    def to_model(dto: HourlyRateDTO) -> HourlyRateModel:
        return HourlyRateModel(
            role_code=dto.role_code,
            category=dto.category,
            position=dto.position,
            level=dto.level,
            smb_rate=dto.smb_rate,
            corporate_rate=dto.corporate_rate,
            description=dto.description
        )