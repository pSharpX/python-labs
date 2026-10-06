from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class BusinessLineRoleDTO:
    id: int = field(
        metadata={"description": "ID único de la relación entre la línea de negocio y los roles."}
    )
    business_line: str = field(
        metadata={"description": "Nombre de la línea de negocio (ej. 'Cloud Solutions', 'Cybersecurity')."}
    )
    main_role: Optional[str] = field(
        default=None,
        metadata={"description": "Nombre del rol principal asignado a la línea de negocio."}
    )
    main_role_code: Optional[str] = field(
        default=None,
        metadata={"description": "Código identificador del rol principal (ej. 'DEV-SR-01')."}
    )
    support_roles: Optional[str] = field(
        default=None,
        metadata={"description": "Texto con la lista o descripción de roles de soporte requeridos."}
    )
    support_roles_list: List[str] = field(
        default_factory=list,
        metadata={"description": "Lista de códigos o nombres de roles de soporte parseados para un fácil procesamiento."}
    )
    target_segment: Optional[str] = field(
        default=None,
        metadata={"description": "Segmento de cliente al que aplica (ej. 'SMB', 'CORPORATE' o 'ALL')."}
    )
    usage_description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción del uso y responsabilidades de estos roles en la estimación del servicio."}
    )