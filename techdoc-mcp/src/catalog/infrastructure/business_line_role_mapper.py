from typing import List, Optional

from src.catalog.domain.business_line_role import BusinessLineRoleDTO
from src.catalog.models.business_line_role import BusinessLineRoleModel


class BusinessLineRoleMapper:
    @staticmethod
    def _parse_support_roles(support_roles_text: Optional[str]) -> List[str]:
        """Convierte una cadena separada por comas en una lista limpia de roles."""
        if not support_roles_text:
            return []
        return [role.strip() for role in support_roles_text.split(",") if role.strip()]

    @classmethod
    def to_dto(cls, model: BusinessLineRoleModel) -> BusinessLineRoleDTO:
        """Convierte el modelo SQLAlchemy a DTO enriquecido."""
        return BusinessLineRoleDTO(
            id=model.id,
            business_line=model.business_line,
            main_role=model.main_role,
            main_role_code=model.main_role_code,
            support_roles=model.support_roles,
            support_roles_list=cls._parse_support_roles(model.support_roles),
            target_segment=model.target_segment,
            usage_description=model.usage_description
        )