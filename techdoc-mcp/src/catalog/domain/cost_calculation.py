from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class CostCalculationDTO:
    role_code: str = field(
        metadata={"description": "Código identificador único del rol técnico o profesional (ej. DEV-01)."}
    )
    position: str = field(
        metadata={"description": "Nombre o título formal del puesto o perfil profesional."}
    )
    segment: str = field(
        metadata={"description": "Segmento comercial al que aplica el cálculo (ej. SMB o CORPORATIVO)."}
    )
    base_rate: Decimal = field(
        metadata={"description": "Tarifa base por hora asignada al rol en el segmento correspondiente."}
    )
    surcharge_code: Optional[str] = field(
        metadata={
            "description": "Código del recargo aplicado por condiciones especiales (ej. SUR-HOR-01), si corresponde."}
    )
    surcharge_factor: Decimal = field(
        metadata={"description": "Factor o porcentaje multiplicador del recargo aplicado a la tarifa base."}
    )
    hours: Decimal = field(
        metadata={"description": "Cantidad total de horas estimadas o facturables para la prestación del servicio."}
    )
    total_cost: Decimal = field(
        metadata={"description": "Costo final calculado del servicio, incluyendo la tarifa base, horas y recargos."}
    )