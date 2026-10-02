from src.catalog.domain.segmentation_criterion import SegmentationCriterionDTO
from src.catalog.models.segmentation_criterion import SegmentationCriterionModel


class SegmentationCriterionMapper:
    @staticmethod
    def to_dto(model: SegmentationCriterionModel) -> SegmentationCriterionDTO:
        """Convierte una entidad SQLAlchemy a DTO genérico."""
        return SegmentationCriterionDTO(
            id=model.id,
            criterion=model.criterion,
            smb_description=model.smb_description,
            corporate_description=model.corporate_description
        )
