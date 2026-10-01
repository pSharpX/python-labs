from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.shared import ArchitectureComponent, TechnologyDecision, TechnicalIntegration, ScalabilityDesign, SecurityDesign, \
    AvailabilityDesign, ObservabilityDesign, DeploymentDesign, DataArchitecture, DocumentationSource


class TechArchitectOutputSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "description": "Esquema estructurado para la propuesta técnica-funcional y de arquitectura."
        },
    )

    solution_overview: str = Field(
        description="Resumen ejecutivo claro y conciso de la arquitectura propuesta, destacando cómo satisface las necesidades del negocio."
    )
    architecture_components: list[ArchitectureComponent] = Field(
        default_factory=list,
        description="Componentes o módulos principales que conforman la solución arquitectónica.",
    )
    technology_decisions: list[TechnologyDecision] = Field(
        default_factory=list,
        description="Decisiones tecnológicas clave (lenguajes, frameworks, bases de datos) junto con su justificación técnica.",
    )
    integrations: list[TechnicalIntegration] = Field(
        default_factory=list,
        description="Detalle de las integraciones técnicas con sistemas internos, externos o APIs de terceros.",
    )
    security: SecurityDesign | None = Field(
        default=None,
        description="Estrategia y mecanismos de seguridad (autenticación, autorización, cifrado, cumplimiento normativo).",
    )
    scalability: ScalabilityDesign | None = Field(
        default=None,
        description="Diseño para el escalamiento horizontal/vertical, manejo de carga y elasticidad de la arquitectura.",
    )
    availability: AvailabilityDesign | None = Field(
        default=None,
        description="Estrategia para garantizar la alta disponibilidad, tolerancia a fallos y recuperación ante desastres (DRP/HA).",
    )
    observability: ObservabilityDesign | None = Field(
        default=None,
        description="Estrategias e instrumentos de monitoreo, centralización de logs, trazabilidad distribuida y métricas.",
    )
    deployment: DeploymentDesign | None = Field(
        default=None,
        description="Estrategia de despliegue, infraestructura como código (IaC), contenedores y pipeline CI/CD.",
    )
    data_architecture: DataArchitecture | None = Field(
        default=None,
        description="Modelo y flujo de datos, estrategias de almacenamiento, persistencia, caché y migración de datos.",
    )
    implementation_approach: list[str] = Field(
        default_factory=list,
        description="Estrategia y fases o roadmap técnico recomendado para la implementación gradual del proyecto.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Supuestos y premisas técnicas consideradas verdaderas para fundamentar este diseño arquitectónico.",
    )
    technical_risks: list[str] = Field(
        default_factory=list,
        description="Riesgos técnicos identificados que podrían impactar el desarrollo o la operación, junto a sus mitigaciones.",
    )
    documentation_sources: list[DocumentationSource] = Field(
        default_factory=list,
        description="Referencias o fuentes de documentación utilizadas o requeridas para este diseño.",
    )
    technical_proposal: str = Field(
        description="Propuesta o narrativa técnica global consolidada en formato de texto extenso (ej. Markdown) que resume toda la arquitectura."
    )

    @model_validator(mode="before")
    @classmethod
    def handle_nested_wrapper(cls, data: Any) -> Any:
        """
        Garantiza compatibilidad si el LLM envuelve por error toda la respuesta
        dentro de una clave 'technical_proposal'.
        """
        if isinstance(data, dict):
            # Si el LLM devolvió {'technical_proposal': {'solution_overview': ...}}
            if (
                    "technical_proposal" in data
                    and isinstance(data["technical_proposal"], dict)
                    and "solution_overview" in data["technical_proposal"]
            ):
                return data["technical_proposal"]
        return data