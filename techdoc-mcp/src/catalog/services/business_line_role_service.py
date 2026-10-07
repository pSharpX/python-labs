import logging
from typing import List, Optional, Dict, Set

from src.catalog.domain.role_detail import RoleDetailDTO
from src.catalog.models.business_line_role import BusinessLineRoleModel
from src.catalog.database import SessionFactory
from src.catalog.domain.business_line_role import BusinessLineRoleDTO
from src.catalog.infrastructure.business_line_role_mapper import BusinessLineRoleMapper
from src.catalog.repositories.business_line_role_repository import BusinessLineRoleRepository
from src.catalog.repositories.hourly_rate_repository import HourlyRateRepository

logger = logging.getLogger(__name__)


class BusinessLineRoleService:
    def __init__(self):
        self.session = SessionFactory()
        self.repository = BusinessLineRoleRepository(self.session)
        self.hourly_rate_repository = HourlyRateRepository(self.session)

    def _fetch_roles_details_map(self, models: List[BusinessLineRoleModel]) -> Dict[str, RoleDetailDTO]:
        """Extrae todos los códigos de roles de soporte, consulta la tabla de tarifas y genera un mapa por role_code."""
        role_codes: Set[str] = set()
        for m in models:
            role_codes.update(BusinessLineRoleMapper.parse_support_roles(m.support_roles))

        if not role_codes:
            return {}

        # Consulta los modelos de la tabla hourly_rate
        hourly_rate_models = self.hourly_rate_repository.get_by_role_codes(list(role_codes))

        # Construye el mapa clave-valor
        details_map: Dict[str, RoleDetailDTO] = {}
        for hr in hourly_rate_models:
            details_map[hr.role_code] = RoleDetailDTO(
                role_code=hr.role_code,
                category=getattr(hr, "category", None),
                position=getattr(hr, "position", None),
                level=getattr(hr, "level", None),
                description=getattr(hr, "description", None)
            )

        return details_map

    def get_roles_by_business_line(
            self, business_line: str, segment: Optional[str] = None
    ) -> List[BusinessLineRoleDTO]:
        """
        Obtiene los roles necesarios (principales y de soporte) para una línea de negocio,
        opcionalmente filtrado por segmento comercial.
        """
        logger.info(f">> Obteniendo roles para línea de negocio='{business_line}' (segmento={segment})")

        models = self.repository.get_by_business_line(business_line)
        # if segment:
        #     models = self.repository.get_by_business_line_and_segment(business_line, segment)
        # else:
        #     models = self.repository.get_by_business_line(business_line)
        roles_details_map = self._fetch_roles_details_map(list(models))

        return [
            BusinessLineRoleMapper.to_dto(model, roles_details_map)
            for model in models
        ]

    def get_all_business_line_roles(self) -> List[BusinessLineRoleDTO]:
        """Recupera el catálogo completo de líneas de negocio y sus roles requeridos."""
        logger.info(">> Obteniendo el catálogo completo de roles por línea de negocio")
        models = self.repository.get_all()
        return [BusinessLineRoleMapper.to_dto(model, {}) for model in models]