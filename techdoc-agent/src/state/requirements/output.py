from pydantic import BaseModel, ConfigDict, Field

from src.shared import (Actor, Process, Integration, ProposalScope, MissingInformation,
                        NonFunctionalRequirement, Requirement, ClientQuestion)


class RequirementsOutputSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "description": "Esquema estructurado para el análisis y extracción de requerimientos de clientes."
        },
    )

    problem_statement: str | None = Field(
        default=None,
        description="Descripción clara y concisa del problema de negocio que el cliente busca resolver.",
    )
    business_objectives: list[str] = Field(
        default_factory=list,
        description="Lista de objetivos cuantitativos y cualitativos de negocio que se esperan alcanzar con la solución.",
    )

    expected_results: list[str] = Field(
        default_factory=list,
        description="Resultados concretos, entregables o beneficios esperados al finalizar la implementación.",
    )
    actors: list[Actor] = Field(
        default_factory=list,
        description="Lista de actores, roles o sistemas externos que interactúan con el sistema.",
    )
    business_processes: list[Process] = Field(
        default_factory=list,
        description="Procesos de negocio actuales o futuros involucrados dentro del alcance del proyecto.",
    )

    functional_requirements: list[Requirement] = Field(
        default_factory=list,
        description="Requerimientos funcionales específicos detallando las capacidades que debe ofrecer el sistema.",
    )
    non_functional_requirements: list[NonFunctionalRequirement] = Field(
        default_factory=list,
        description="Requerimientos no funcionales (desempeño, seguridad, disponibilidad, escalabilidad, mantenibilidad).",
    )

    business_rules: list[str] = Field(
        default_factory=list,
        description="Reglas de negocio, políticas o restricciones normativas que condicionan el comportamiento del sistema.",
    )
    integrations: list[Integration] = Field(
        default_factory=list,
        description="Sistemas, APIs o bases de datos externas con las que el sistema debe integrarse.",
    )

    data_and_volumetrics: list[str] = Field(
        default_factory=list,
        description="Estimaciones de volumen de datos, usuarios concurrentes, almacenamiento y patrones de crecimiento.",
    )
    scope: ProposalScope | None = Field(
        default=None,
        description="Definición explícita de lo que está dentro (In-Scope) y fuera (Out-of-Scope) del alcance del proyecto.",
    )

    assumptions: list[str] = Field(
        default_factory=list,
        description="Supuestos clave aceptados para la elaboración de la propuesta técnica y funcional.",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Factores, sistemas o aprobaciones externas requeridas para el éxito del proyecto.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Limitaciones técnicas, temporales, presupuestales, normativas o de recursos imposición del cliente.",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Riesgos identificados que podrían impactar el costo, tiempo, alcance o calidad de la solución.",
    )

    missing_information: list[MissingInformation] = Field(
        default_factory=list,
        description="Lista de vacíos de información o ambigüedades identificadas en la solicitud inicial del cliente.",
    )
    client_questions: list[ClientQuestion] = Field(
        default_factory=list,
        description="Preguntas específicas y aclaratorias dirigidas al cliente para resolver ambigüedades técnicas o de negocio.",
    )
    ready_for_architecture: bool = Field(
        default=False,
        description="Indica si la información proporcionada es suficiente y clara para proceder al diseño de la arquitectura técnica.",
    )

    readiness_reason: str = Field(
        default="",
        description="Justificación detallada de por qué el proyecto está o no está listo para continuar a la fase de arquitectura técnica.",
    )