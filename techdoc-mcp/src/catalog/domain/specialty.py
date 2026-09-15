from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SpecialtyDTO:
    code: str = field(
        metadata={"description": "Código identificador único de la especialidad técnica."}
    )
    name: str = field(
        metadata={"description": "Nombre descriptivo de la especialidad (ej. Cloud & Infraestructura, DevOps)."}
    )
    code_example: Optional[str] = field(
        metadata={"description": "Ejemplo o referencia de código asociado a esta especialidad."}
    )