from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class RoleDetailDTO:
    role_code: str = field(
        metadata={
            "description": (
                "Código estandarizado del rol. Sigue la estructura "
                "'HH' + 'ROL_O_TECNOLOGÍA' + 'NIVEL_OPCIONAL' (ej. HH-DEV-SR, HH-QA, HH-ARQ)."
            )
        }
    )
    category: Optional[str] = field(
        default=None,
        metadata={"description": "Categoría o área técnica del rol (ej. 'Desarrollo', 'Arquitectura', 'Gestión')."}
    )
    position: Optional[str] = field(
        default=None,
        metadata={"description": "Nombre o título formal del puesto de trabajo."}
    )
    level: Optional[str] = field(
        default=None,
        metadata={"description": "Nivel de seniority o experiencia asignado (ej. 'Junior', 'Semi-Senior', 'Senior')."}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción detallada de las responsabilidades y alcances de la posición."}
    )
