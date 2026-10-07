from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.shared import (Architecture, ArchitectureComponent, TechnologyDecision, TechnicalIntegration, ScalabilityDesign,
                        SecurityDesign, AvailabilityDesign, ObservabilityDesign, DeploymentDesign, DataArchitecture,
                        DocumentationSource, ServiceClassification, ProjectPhase, ResourceProfile, TimelineEstimation)


class TechArchitectOutputSchema(BaseModel):
    """
    Esquema estructurado consolidado para la propuesta técnica-funcional y el diseño
    de arquitectura de software.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
        json_schema_extra={
            "description": "Esquema estructurado para la propuesta técnica-funcional y de arquitectura."
        },
    )

    architecture: Architecture | None = Field(
        default=None,
        description="Definición y detalles del diseño arquitectónico de la solución (estilo, síntesis y diagrama Mermaid).",
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
    implementation_approach: str | None = Field(
        default=None,
        description="Descripción ejecutiva de la estrategia de implementación y secuencia recomendada."
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Supuestos y premisas técnicas consideradas verdaderas para fundamentar este diseño arquitectónico.",
    )
    # 8. Prerequisites
    prerequisites: list[str] = Field(
        default_factory=list,
        description="Condiciones, insumos o accesos previos que deben cumplirse antes de iniciar el trabajo.",
    )
    technical_risks: list[str] = Field(
        default_factory=list,
        description="Riesgos técnicos identificados que podrían impactar el desarrollo o la operación, junto a sus mitigaciones.",
    )
    documentation_sources: list[DocumentationSource] = Field(
        default_factory=list,
        description="Referencias o fuentes de documentación utilizadas o requeridas para este diseño.",
    )
    # 1. Service Classification & Identification
    service_classification: ServiceClassification = Field(
        description="Clasificación del servicio, mapeo a opciones del catálogo y alineación de dominio (Línea de Negocio, Segmentación, Producto)."
    )

    # 2, 3 & 4. Solution Phasing, Activity Mapping & Deliverables
    project_phases: list[ProjectPhase] = Field(
        default_factory=list,
        description="Fases estructuradas del proyecto, incluyendo actividades asociadas y entregables concretos por fase.",
    )

    # 5. Resource & Profile Identification
    required_profiles: list[ResourceProfile] = Field(
        default_factory=list,
        description="Perfiles técnicos y funcionales requeridos obtenidos según la regla de dependencia del catálogo.",
    )

    # 6. Project Timeline Estimation
    timeline_estimation: TimelineEstimation = Field(
        description="Estimación global de duración (semanas) y esfuerzo total (horas) para la ejecución del proyecto."
    )
