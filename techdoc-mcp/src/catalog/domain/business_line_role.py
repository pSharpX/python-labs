from dataclasses import dataclass, field
from typing import Optional, List

from src.catalog.domain.role_detail import RoleDetailDTO


@dataclass
class BusinessLineRoleDTO:
    id: int = field(
        metadata={"description": "ID único de la relación entre la línea de negocio y los roles."}
    )
    business_line: str = field(
        metadata={"description": "Nombre de la línea de negocio (ej. 'Cloud e Infraestructura', 'Desarrollo Web y Móvil', 'Ciberseguridad')."}
    )
    main_role: Optional[str] = field(
        default=None,
        metadata={"description": "Nombre del rol principal asignado a la línea de negocio."}
    )
    main_role_code: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "Código identificador del rol principal. Sigue la estructura "
                "'HH' + 'ROL_O_TECNOLOGÍA' + 'NIVEL_OPCIONAL' (ej. HH-DEV-SR, HH-UX, HH-QA, HH-PM, HH-DEV, HH-ARQ)."
            )
        }
    )
    support_roles: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "Cadena de texto con los roles secundarios o de soporte, codificados bajo la "
                "convención 'HH' + 'ROL_O_TECNOLOGÍA' + 'NIVEL_OPCIONAL' y separados por punto y coma."
            )
        }
    )
    support_roles_list: List[RoleDetailDTO] = field(
        default_factory=list,
        metadata={
            "description": (
                "Lista detallada con la información enriquecida de cada rol de soporte "
                "(código, categoría, puesto, nivel y descripción), consultada desde las tarifas por hora."
            )
        }
    )
    target_segment: Optional[str] = field(
        default=None,
        metadata={"description": "Segmento de cliente al que aplica (ej. 'SMB', 'CORPORATE' o 'ALL')."}
    )
    usage_description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción del uso y responsabilidades de estos roles en la estimación del servicio."}
    )