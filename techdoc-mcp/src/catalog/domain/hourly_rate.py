from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class HourlyRateDTO:
    role_code: str = field(
        metadata={"description": "Código identificador único del rol o perfil profesional."}
    )
    category: str = field(
        metadata={"description": "Categoría o especialidad a la que pertenece el rol (ej. Arquitectura, Desarrollo)."}
    )
    position: str = field(
        metadata={"description": "Nombre del puesto o cargo desempeñado por el especialista."}
    )
    level: Optional[str] = field(
        metadata={"description": "Nivel de experiencia o seniority del rol (ej. Junior, Semi-Senior, Senior)."}
    )
    smb_rate: Decimal = field(
        metadata={"description": "Tarifa por hora configurada para el segmento SMB."}
    )
    corporate_rate: Decimal = field(
        metadata={"description": "Tarifa por hora configurada para el segmento Corporativo."}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción detallada sobre las responsabilidades y alcances del rol."}
    )