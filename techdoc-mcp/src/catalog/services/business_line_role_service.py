import logging
from typing import List, Optional

from catalog.database import SessionFactory
from catalog.domain.business_line_role import BusinessLineRoleDTO
from catalog.infrastructure.business_line_role_mapper import BusinessLineRoleMapper
from catalog.repositories.business_line_role_repository import BusinessLineRoleRepository

logger = logging.getLogger(__name__)


class BusinessLineRoleService:
    def __init__(self):
        self.session = SessionFactory()
        self.repository = BusinessLineRoleRepository(self.session)

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

        return [BusinessLineRoleMapper.to_dto(model) for model in models]

    def get_all_business_line_roles(self) -> List[BusinessLineRoleDTO]:
        """Recupera el catálogo completo de líneas de negocio y sus roles requeridos."""
        logger.info(">> Obteniendo el catálogo completo de roles por línea de negocio")
        models = self.repository.get_all()
        return [BusinessLineRoleMapper.to_dto(model) for model in models]