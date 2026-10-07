from typing import List, Optional, Dict

from src.catalog.domain.role_detail import RoleDetailDTO
from src.catalog.domain.business_line_role import BusinessLineRoleDTO
from src.catalog.models.business_line_role import BusinessLineRoleModel


class BusinessLineRoleMapper:
    @staticmethod
    def parse_support_roles(support_roles_text: Optional[str]) -> List[str]:
        """Convierte una cadena separada por punto y coma en una lista limpia de roles."""
        if not support_roles_text:
            return []
        return [role.strip() for role in support_roles_text.split(";") if role.strip()]

    @classmethod
    def to_dto(
            cls,
            model: BusinessLineRoleModel,
            roles_details_map: Dict[str, RoleDetailDTO]
    ) -> BusinessLineRoleDTO:
        """Convierte la entidad en DTO asociando los detalles de cada rol de soporte."""
        raw_codes = cls.parse_support_roles(model.support_roles)

        # Mapea cada código a su DTO enriquecido o crea uno básico con el código si no existe en la BD
        detailed_support_roles = [
            roles_details_map.get(
                code,
                RoleDetailDTO(role_code=code, category=None, position=None, level=None, description=None)
            )
            for code in raw_codes
        ]
        return BusinessLineRoleDTO(
            id=model.id,
            business_line=model.business_line,
            main_role=model.main_role,
            main_role_code=model.main_role_code,
            support_roles=model.support_roles,
            support_roles_list=detailed_support_roles,
            target_segment=model.target_segment,
            usage_description=model.usage_description
        )