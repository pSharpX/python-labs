from dataclasses import dataclass, field
from typing import List


@dataclass
class FamilyDTO:
    id: int = field(
        metadata={
            "description": "ID único identificador de la familia en base de datos."
        }
    )

    name: str = field(
        metadata={
            "description": "Nombre de la familia de productos/servicios."
        }
    )