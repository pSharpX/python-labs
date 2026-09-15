from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class SurchargeDTO:
    code: str = field(
        metadata={"description": "Código identificador único del recargo o condición tarifaria especial."}
    )
    condition: str = field(
        metadata={
            "description": "Descripción de la condición que activa el recargo (ej. Horarios nocturnos, Trabajos en feriados)."}
    )
    factor: Decimal = field(
        metadata={"description": "Valor numérico o multiplicador que modifica la tarifa base."}
    )
    rule: Optional[str] = field(
        default=None,
        metadata={"description": "Regla o lógica de negocio específica bajo la cual aplica el recargo."}
    )