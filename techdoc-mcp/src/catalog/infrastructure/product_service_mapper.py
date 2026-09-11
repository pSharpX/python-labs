from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.models.product_service import ProductServiceModel


class ProductServiceMapper:
    @staticmethod
    def to_dto(model: ProductServiceModel) -> ProductServiceDTO:
        return ProductServiceDTO(
            id=model.id,
            code=model.code,
            name=model.name,
            type=model.type,
            smb_applicable=model.smb_applicable,
            corp_applicable=model.corp_applicable,
            description=model.description,
            family_name=model.family.name if model.family else "",
            line_name=model.family.business_line.name if model.family and model.family.business_line else ""
        )