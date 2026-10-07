from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, ConfigDict, model_validator

from src.shared import ServiceItem, EffortItem


class FinancialEstimatorOutputSchema(BaseModel):
    """
    Esquema de salida estructurada para la estimación financiera y desglose de costos
    de la propuesta comercial / técnica.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    service_items: list[ServiceItem] = Field(
        default_factory=list,
        description="Lista detallada de ítems de servicio, licencias o entregables incluidos en la propuesta financiera.",
    )
    effort_breakdown: list[EffortItem] = Field(
        default_factory=list,
        description="Desglose del esfuerzo estimado por rol, fase o perfil profesional expresado en horas o jornadas.",
    )
    hourly_rate: Decimal | None = Field(
        default=None,
        description="Tarifa promedio o tarifa hora base aplicada para el cálculo del esfuerzo financiero.",
    )
    estimated_hours: Decimal | None = Field(
        default=None,
        description="Total consolidado de horas estimadas requeridas para la ejecución completa del proyecto.",
    )
    subtotal: Decimal | None = Field(
        default=None,
        description="Monto subtotal antes de la aplicación de impuestos, tasas o descuentos.",
    )
    taxes: Decimal | None = Field(
        default=None,
        description="Monto calculado correspondiente a impuestos (ej. IGV, IVA) aplicables según la jurisdicción.",
    )
    total: Decimal | None = Field(
        default=None,
        description="Monto total consolidado de la propuesta financiera (Subtotal + Impuestos).",
    )
    currency: str = Field(
        default="USD",
        description="Código de moneda ISO 4217 de los montos expresados (ej. 'USD', 'PEN', 'EUR', 'CLP').",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Supuestos, condiciones comerciales o premisas económicas consideradas para la estimación.",
    )
    financial_proposal: str = Field(
        description="Propuesta comercial o resumen ejecutivo financiero consolidado en formato de texto o Markdown.",
    )

    @model_validator(mode="before")
    @classmethod
    def handle_nested_wrapper(cls, data: Any) -> Any:
        """
        Garantiza compatibilidad si el LLM envuelve por error toda la respuesta
        dentro de una clave 'financial_proposal' u otra clave contenedora.
        """
        if isinstance(data, dict):
            # Si el LLM devolvió {'financial_proposal': {'service_items': ...}}
            if (
                    "financial_proposal" in data
                    and isinstance(data["financial_proposal"], dict)
                    and (
                    "service_items" in data["financial_proposal"]
                    or "subtotal" in data["financial_proposal"]
            )
            ):
                return data["financial_proposal"]
        return data