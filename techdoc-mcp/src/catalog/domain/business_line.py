from dataclasses import dataclass, field
from typing import Optional, List


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
    main_families: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción o texto de las familias de productos/servicios principales asociadas."}
    )
    main_families_list: List[str] = field(
        default_factory=list,
        metadata={"description": "Lista parseada de las familias principales para fácil lectura del modelo."}
    )