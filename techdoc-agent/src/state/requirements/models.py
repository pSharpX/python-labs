from typing import Literal

from pydantic import Field, BaseModel

from src.shared.constants import Priority


class Requirement(BaseModel):
    id: str
    description: str
    priority: Priority = "to_be_defined"

    actor: str | None = None
    process: str | None = None

    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    source: str | None = None
    confirmed: bool = False

class NonFunctionalRequirement(BaseModel):
    id: str
    category: str
    description: str
    priority: Priority = "to_be_defined"

    acceptance_criteria: list[str] = Field(default_factory=list)

    source: str | None = None
    confirmed: bool = False

class Actor(BaseModel):
    name: str
    type: str
    responsibility: str
    source: str | None = None

class Process(BaseModel):
    name: str
    objective: str
    actors: list[str] = Field(default_factory=list)

    main_flow: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    result: str | None = None

class Integration(BaseModel):
    system: str
    purpose: str
    data: list[str] = Field(default_factory=list)

    direction: str | None = None
    frequency: str | None = None
    status: str = "por confirmar"

class Risk(BaseModel):
    description: str
    impact: str
    cause: str
    action_validation: str

class Assumption(BaseModel):
    description: str
    requires_validation: bool = True
    source: str | None = None

class MissingInformation(BaseModel):
    description: str
    criticality: Literal[
        "critical",
        "important",
        "desirable",
    ]
    reason: str | None

class ClientQuestion(BaseModel):
    question: str
    reason: str
    related_to: str | None = None

class ProposalScope(BaseModel):
    included: list[str] = Field(default_factory=list)
    excluded: list[str] = Field(default_factory=list)
    to_confirm: list[str] = Field(default_factory=list)

class Requirements(BaseModel):
    context: str = Field(
        default="",
        description=(
            "Contexto general del cliente, organización o proyecto. "
            "Describe la situación actual, antecedentes relevantes, "
            "área involucrada y cualquier información necesaria para "
            "comprender el requerimiento."
        ),
    )

    problem_need: str = Field(
        default="",
        description=(
            "Problema, necesidad u oportunidad de negocio que origina "
            "el requerimiento. Debe describir qué situación se desea "
            "resolver o qué necesidad se desea atender."
        ),
    )

    objectives: list[str] = Field(
        default_factory=list,
        description=(
            "Objetivos que se espera alcanzar con la solución. "
            "Cada elemento debe representar un objetivo concreto, "
            "relevante y relacionado con el problema o necesidad identificada."
        ),
    )

    expected_results: list[str] = Field(
        default_factory=list,
        description=(
            "Resultados esperados después de implementar la solución. "
            "Describe los cambios, capacidades, entregables o beneficios "
            "que deberían obtenerse."
        ),
    )

    actors: list[Actor] = Field(
        default_factory=list,
        description=(
            "Personas, roles, áreas, sistemas u otras entidades que "
            "participan, interactúan o se ven afectadas por la solución. "
            "Incluye tanto actores internos como externos cuando corresponda."
        ),
    )

    processes: list[Process] = Field(
        default_factory=list,
        description=(
            "Procesos de negocio o procesos operativos relacionados con "
            "el problema y la solución. Describe los procesos actuales "
            "o los que deberán ser soportados por la solución."
        ),
    )

    functional_requirements: list[Requirement] = Field(
        default_factory=list,
        description=(
            "Funcionalidades o comportamientos que la solución debe "
            "proporcionar. Cada requerimiento debe describir una capacidad "
            "observable y verificable del sistema o servicio."
        ),
    )

    non_functional_requirements: list[NonFunctionalRequirement] = Field(
        default_factory=list,
        description=(
            "Requisitos de calidad, rendimiento, seguridad, disponibilidad, "
            "escalabilidad, mantenibilidad, cumplimiento u otras características "
            "no funcionales que debe cumplir la solución."
        ),
    )

    business_rules: list[str] = Field(
        default_factory=list,
        description=(
            "Reglas, políticas, condiciones o restricciones de negocio "
            "que determinan cómo deben ejecutarse los procesos o "
            "comportarse la solución."
        ),
    )

    integrations: list[Integration] = Field(
        default_factory=list,
        description=(
            "Sistemas, aplicaciones, servicios, APIs, plataformas o fuentes "
            "externas con las que la solución debe intercambiar información "
            "o interactuar."
        ),
    )

    data_and_volumetrics: list[str] = Field(
        default_factory=list,
        description=(
            "Información relacionada con los datos utilizados por la solución "
            "y sus volúmenes estimados. Puede incluir cantidad de registros, "
            "usuarios, transacciones, frecuencia, tamaño de datos, crecimiento "
            "esperado y otros indicadores relevantes."
        ),
    )

    scope: ProposalScope | None = Field(
        default=None,
        description=(
            "Alcance de la solución propuesta. Define qué componentes, "
            "funcionalidades, procesos, sistemas o actividades están incluidos "
            "y, cuando esté disponible, qué elementos quedan fuera del alcance."
        ),
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description=(
            "Dependencias que deben cumplirse para implementar u operar "
            "la solución. Pueden incluir sistemas externos, equipos, "
            "proveedores, información, decisiones, accesos, infraestructura "
            "u otros factores externos."
        ),
    )

    constraints: list[str] = Field(
        default_factory=list,
        description=(
            "Restricciones conocidas que limitan el diseño, implementación "
            "u operación de la solución. Pueden incluir restricciones técnicas, "
            "de arquitectura, seguridad, regulación, tiempo, recursos, "
            "tecnología o políticas."
        ),
    )

    risks: list[Risk] = Field(
        default_factory=list,
        description=(
            "Riesgos identificados que podrían afectar el alcance, costo, "
            "cronograma, calidad, seguridad o viabilidad de la solución. "
            "Incluye la descripción del riesgo y la información disponible "
            "sobre su impacto o probabilidad."
        ),
    )

    assumptions: list[Assumption] = Field(
        default_factory=list,
        description=(
            "Supuestos utilizados para completar o interpretar el análisis "
            "cuando no existe información confirmada. Los supuestos deben "
            "diferenciarse claramente de los hechos proporcionados por el cliente."
        ),
    )

    # missing_information: list[MissingInformation] = Field(
    #     default_factory=list,
    #     description=(
    #         "Información relevante que aún no está disponible o no ha sido "
    #         "confirmada y que puede ser necesaria para completar el análisis "
    #         "de requerimientos o diseñar la solución."
    #     ),
    # )
    #
    # client_questions: list[ClientQuestion] = Field(
    #     default_factory=list,
    #     description=(
    #         "Preguntas que deben realizarse al cliente para aclarar "
    #         "ambigüedades, validar supuestos, completar información faltante "
    #         "o tomar decisiones necesarias para continuar con el análisis."
    #     ),
    # )

    @classmethod
    def from_state(cls, state: dict) -> "Requirements":
        return cls(
            context=state.get("context", ""),
            problem_need=state.get("problem_need", ""),
            objectives=state.get("objectives", []),
            expected_results=state.get("expected_results", []),
            actors=state.get("actors", []),
            processes=state.get("processes", []),
            functional_requirements=state.get(
                "functional_requirements", []
            ),
            non_functional_requirements=state.get(
                "non_functional_requirements", []
            ),
            business_rules=state.get("business_rules", []),
            integrations=state.get("integrations", []),
            data_and_volumetrics=state.get(
                "data_and_volumetrics", []
            ),
            scope=state.get("scope"),
            dependencies=state.get("dependencies", []),
            constraints=state.get("constraints", []),
            risks=state.get("risks", []),
            assumptions=state.get("assumptions", []),
            # missing_information=state.get(
            #     "missing_information", []
            # ),
            # client_questions=state.get(
            #     "client_questions", []
            # ),
        )
