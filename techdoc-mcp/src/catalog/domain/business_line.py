from dataclasses import dataclass, field
from typing import Optional, List

from src.catalog.domain.family import FamilyDTO


@dataclass
class BusinessLineDTO:
    id: int = field(
        metadata={"description": "ID único identificador de la línea de negocio en base de datos."}
    )
    code: int = field(
        metadata={"description": "Código numérico único asignado a la línea de negocio (ej. 101, 202)."}
    )
    name: str = field(
        metadata={"description": "Nombre de la línea de negocio (ej. 'Cloud & Infraestructura', 'Ciberseguridad')."}
    )

    families: List[FamilyDTO] = field(
        default_factory=list,
        metadata={
            "description": (
                "Lista de familias de productos/servicios asociadas a esta "
                "línea de negocio. Cada familia contiene únicamente su ID y nombre."
            )
        }
    )