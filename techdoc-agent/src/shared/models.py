from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Literal, List, Optional, Self

from pydantic import Field, BaseModel, model_validator, ConfigDict

from .enums import UserAction
from .constants import Priority, ServiceCategory


class ProposalStatus(str, Enum):
    INITIALIZING = "initializing"
    ANALYZING_REQUIREMENTS = "analyzing_requirements"
    AWAITING_REQUIREMENTS = "awaiting_requirements"
    REQUIREMENTS_READY = "requirements_ready"
    BUILDING_TECHNICAL_PROPOSAL = "building_technical_proposal"
    TECHNICAL_PROPOSAL_READY = "technical_proposal_ready"
    BUILDING_FINANCIAL_PROPOSAL = "building_financial_proposal"
    AWAITING_FINANCIAL_APPROVAL = "awaiting_financial_approval"
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    ERROR = "error"
    COMPLETED = "completed"

class UserApprovalAction(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REVISE_REQUIREMENTS = "revise_requirements"

# --- Revision Tracking ---
class ProposalRevision(BaseModel):
    revision: int
    changed_by: str
    changed_fields: List[str]
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserResponse(BaseModel):
    """What a human sends when resuming an interrupted workflow."""

    action: UserAction
    feedback: str | None = None  # request_changes
    information: str | None = None  # provide_information
    changes: str | None = None  # change_requirements
    changed_by: str = "user"
    reason: str | None = None

    @model_validator(mode="after")
    def _required_payload(self) -> Self:
        needed = {
            UserAction.REQUEST_CHANGES: "feedback",
            UserAction.PROVIDE_INFORMATION: "information",
            UserAction.CHANGE_REQUIREMENTS: "changes",
        }.get(self.action)
        if needed and not (getattr(self, needed) or "").strip():
            raise ValueError(f"action '{self.action.value}' requires a non-empty '{needed}'")
        return self

class PendingInput(BaseModel):
    """Free text from the user waiting to be folded into the requirements."""

    kind: Literal["clarification", "change"]
    text: str
    changed_by: str = "user"
    reason: str | None = None

class Requirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        description="Identificador único del requerimiento (ej. 'RF-001')."
    )
    description: str = Field(
        description="Descripción clara, concisa y orientada a la acción de lo que el sistema debe hacer."
    )
    priority: Priority = Field(
        default="to_be_defined",
        description="Nivel de prioridad o urgencia del requerimiento para el proyecto.",
    )

    actor: str | None = Field(
        default=None,
        description="Nombre del actor o rol principal que interactúa con este requerimiento.",
    )
    process: str | None = Field(
        default=None,
        description="Nombre del proceso de negocio al que pertenece o respalda este requerimiento.",
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Criterios verificables que determinan si el requerimiento ha sido implementado exitosamente.",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="IDs o descripciones de otros requerimientos o componentes necesarios para este requerimiento.",
    )

    source: str | None = Field(
        default=None,
        description="Origen o referencia en el texto original del cliente de donde se extrajo este requerimiento.",
    )
    confirmed: bool = Field(
        default=False,
        description="Indica si el requerimiento ha sido explícitamente confirmado por el cliente o si es una inferencia.",
    )

class NonFunctionalRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        description="Identificador único del requerimiento no funcional (ej. 'RNF-001')."
    )
    category: str = Field(
        description="Categoría del requerimiento no funcional (ej. 'Seguridad', 'Rendimiento', 'Disponibilidad', 'Escalabilidad', 'Mantenibilidad')."
    )
    description: str = Field(
        description="Detalle del atributo de calidad o restricción técnica exigida al sistema."
    )
    priority: Priority = Field(
        default="to_be_defined",
        description="Nivel de prioridad del requerimiento no funcional.",
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Métricas o criterios cuantitativos/cualitativos para validar este requerimiento (ej. 'Tiempo de respuesta menor a 200ms').",
    )

    source: str | None = Field(
        default=None,
        description="Origen o referencia dentro de la solicitud del cliente.",
    )
    confirmed: bool = Field(
        default=False,
        description="Indica si esta restricción o métrica está confirmada por el cliente.",
    )

class Actor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="Nombre del actor, rol de usuario o sistema externo (ej. 'Administrador', 'Sistema ERP')."
    )
    type: str = Field(
        description="Tipo de actor (ej. 'Usuario final', 'Administrador de sistema', 'Sistema externo', 'Batch process')."
    )
    responsibility: str = Field(
        description="Descripción de la responsabilidad o rol principal del actor dentro de la solución."
    )
    source: str | None = Field(
        default=None,
        description="Origen o mención del actor en el requerimiento del cliente.",
    )

class Process(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="Nombre del proceso de negocio (ej. 'Procesamiento de órdenes de compra')."
    )
    objective: str = Field(
        description="Objetivo de negocio que persigue la ejecución de este proceso."
    )
    actors: list[str] = Field(
        default_factory=list,
        description="Lista de actores o roles que participan directamente en la ejecución de este proceso.",
    )

    main_flow: list[str] = Field(
        default_factory=list,
        description="Secuencia paso a paso del flujo principal o 'camino feliz' del proceso.",
    )
    exceptions: list[str] = Field(
        default_factory=list,
        description="Escenarios alternativos, errores o desviaciones respecto al flujo principal.",
    )
    result: str | None = Field(
        default=None,
        description="Resultado esperado o estado final del negocio al completar exitosamente el proceso.",
    )

class Integration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system: str = Field(
        description="Nombre del sistema objetivo o API con el cual se realizará la integración."
    )
    purpose: str = Field(
        description="Propósito técnico o de negocio de la integración (ej. 'Sincronizar inventario')."
    )
    data: list[str] = Field(
        default_factory=list,
        description="Tipos de datos o entidades intercambiadas a través de la integración (ej. ['Clientes', 'Facturas']).",
    )
    direction: str | None = Field(
        default=None,
        description="Dirección del flujo de datos (ej. 'Entrante', 'Saliente', 'Bidireccional').",
    )
    frequency: str | None = Field(
        default=None,
        description="Frecuencia o patrón de comunicación (ej. 'Tiempo real', 'Batch diario', 'Event-driven').",
    )
    status: str = Field(
        default="por confirmar",
        description="Estado de definición técnica de la integración (ej. 'Definido', 'Por confirmar', 'Deprecado').",
    )

class Risk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(
        description="Descripción detallada del riesgo o evento incierto identificable."
    )
    impact: str = Field(
        description="Efecto o consecuencia negativa en el proyecto si el riesgo se materializa (ej. 'Alto', 'Desviación de tiempo', 'Costo adicional')."
    )
    cause: str = Field(
        description="Causa raíz o factor desencadenante del riesgo."
    )
    action_validation: str = Field(
        description="Acción propuesta para mitigar, prevenir o validar el riesgo con el cliente."
    )

class Assumption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(
        description="Premisa o supuesto considerado como verdadero para avanzar con la propuesta."
    )
    requires_validation: bool = Field(
        default=True,
        description="Indica si el supuesto requiere ser confirmado o aceptado explícitamente por el cliente.",
    )
    source: str | None = Field(
        default=None,
        description="Origen o contexto del que surge el supuesto.",
    )

class MissingInformation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(
        description="Detalle de la información no proporcionada o vacíos conceptuales detectados."
    )
    criticality: Literal["critical", "important", "desirable"] = Field(
        description="Nivel de criticidad del vacío de información para la estimación y diseño arquitectónico."
    )
    reason: str | None = Field(
        default=None,
        description="Explicación de por qué esta información faltante afecta la fase actual de la propuesta.",
    )

class ClientQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        description="Pregunta concreta, clara y formal formulada directamente para el cliente."
    )
    reason: str = Field(
        description="Justificación técnica o de negocio de por qué es indispensable realizar esta pregunta."
    )
    related_to: str | None = Field(
        default=None,
        description="Elemento, proceso, requerimiento o sección del proyecto con el que se relaciona la pregunta.",
    )

class ProposalScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    included: list[str] = Field(
        default_factory=list,
        description="Lista explícita de entregables, funcionalidades o componentes incluidos dentro del alcance (In-Scope).",
    )
    excluded: list[str] = Field(
        default_factory=list,
        description="Lista explícita de funcionalidades, integraciones o actividades que NO forman parte del alcance (Out-of-Scope).",
    )
    to_confirm: list[str] = Field(
        default_factory=list,
        description="Elementos pendientes de validación o decisión por parte del cliente para determinar si entran en el alcance.",
    )

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

    missing_information: list[MissingInformation] = Field(
        default_factory=list,
        description=(
            "Información relevante que aún no está disponible o no ha sido "
            "confirmada y que puede ser necesaria para completar el análisis "
            "de requerimientos o diseñar la solución."
        ),
    )

    client_questions: list[ClientQuestion] = Field(
        default_factory=list,
        description=(
            "Preguntas que deben realizarse al cliente para aclarar "
            "ambigüedades, validar supuestos, completar información faltante "
            "o tomar decisiones necesarias para continuar con el análisis."
        ),
    )

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
            missing_information=state.get(
                "missing_information", []
            ),
            client_questions=state.get(
                "client_questions", []
            ),
        )

class Architecture(BaseModel):
    """
    Representa el estilo arquitectónico general, la síntesis del diseño de software
    y su representación gráfica en código Mermaid.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    style: str = Field(
        description="Estilo o patrón arquitectónico principal seleccionado (ej. 'Monolito Modular', 'Microservicios Event-Driven', 'Serverless', 'Hexagonal')."
    )
    summary: str = Field(
        description="Resumen o síntesis ejecutiva del diseño arquitectónico, explicando sus principios clave y cómo soporta los requerimientos."
    )
    mermaid_diagram: str | None = Field(
        default=None,
        description="Código o sintaxis del diagrama arquitectónico en formato Mermaid.js (ej. 'graph TD; A[Cliente] --> B[API Gateway];').",
    )

class ServiceClassification(BaseModel):
    """
    Clasificación del servicio solicitado y su alineación con el catálogo y dominio del negocio.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    categories: list[ServiceCategory] = Field(
        description="Categorías del servicio identificadas (ej. ['Assessment', 'Design', 'Implementation'])."
    )
    catalog_service_option: str = Field(
        description="Opción o código oficial del Catálogo de Servicios que mejor se alinea con la solicitud."
    )
    business_line: str = Field(
        description="Línea de negocio correspondiente (ej. 'Cloud & Infrastructure', 'Data & AI', 'Cybersecurity')."
    )
    market_segmentation: str = Field(
        description="Segmentación de mercado asociada (ej. 'Enterprise', 'Mid-Market', 'Public Sector')."
    )
    product_or_service: str = Field(
        description="Producto o servicio específico asociado a la propuesta (ej. 'AWS Cloud Migration', 'SAP S/4HANA Consulting')."
    )

class ProjectPhase(BaseModel):
    """
    Fase estructurada del proyecto con sus actividades y entregables clave.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    phase_number: int = Field(
        description="Número secuencial de la fase (ej. 1, 2, 3)."
    )
    name: str = Field(
        description="Nombre de la fase (ej. 'Fase 1: Descubrimiento y Evaluación', 'Fase 2: Diseño de Arquitectura')."
    )
    objective: str = Field(
        description="Objetivo principal a alcanzar durante esta fase del proyecto."
    )
    activities: list[str] = Field(
        default_factory=list,
        description="Lista de actividades y tareas necesarias para ejecutar esta fase.",
    )
    deliverables: list[str] = Field(
        default_factory=list,
        description="Entregables concretos y medibles a producir al finalizar esta fase.",
    )
    estimated_duration_weeks: Decimal | None = Field(
        default=None,
        description="Duración estimada de esta fase en semanas.",
    )

class ResourceProfile(BaseModel):
    """
    Perfil técnico o funcional requerido para el proyecto, consultado desde el catálogo.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    role_title: str = Field(
        description="Título o rol del perfil requerido (ej. 'Arquitecto Cloud Senior', 'DevOps Engineer', 'Consultor Funcional')."
    )
    seniority: str = Field(
        description="Nivel de experiencia requerido (ej. 'Junior', 'Semi-Senior', 'Senior', 'Lead')."
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Responsabilidades principales del perfil dentro del proyecto.",
    )
    estimated_hours: Decimal | None = Field(
        default=None,
        description="Horas estimadas requeridas para este perfil durante la ejecución del proyecto.",
    )

class TimelineEstimation(BaseModel):
    """
    Estimación global de duración, esfuerzo y cronograma general del proyecto.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    total_duration_weeks: Decimal = Field(
        description="Duración total estimada del proyecto expresada en semanas."
    )
    total_effort_hours: Decimal = Field(
        description="Esfuerzo total estimado expresado en horas de trabajo."
    )
    summary: str = Field(
        description="Resumen o descripción del cronograma de alto nivel y sus hitos principales."
    )

class DocumentationSource(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        description="Título o nombre del documento, guía o referencia bibliográfica."
    )
    url: str = Field(
        description="Enlace URL directo a la fuente de documentación o 'N/A' si no aplica."
    )
    source: str = Field(
        description="Origen o autoría de la documentación (ej. 'Documentación Oficial de AWS', 'Repositorio Interno', 'IEEE')."
    )
    relevance: str = Field(
        description="Justificación breve de por qué esta fuente es relevante para la solución arquitectónica."
    )

class ArchitectureComponent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        description="Nombre del componente o módulo dentro del sistema (ej. 'API Gateway', 'Servicio de Autenticación')."
    )
    responsibility: str = Field(
        description="Descripción clara de la responsabilidad única o función principal de este componente."
    )
    technology: str | None = Field(
        default=None,
        description="Tecnología, lenguaje o framework sugerido para implementar el componente (ej. 'Node.js/Express', 'Python/FastAPI').",
    )

class TechnologyDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    decision: str = Field(
        description="Declaración concisa de la tecnología o herramienta seleccionada (ej. 'Uso de PostgreSQL como BD principal')."
    )
    rationale: str = Field(
        description="Justificación técnica e impacto de negocio que respaldan la elección de esta tecnología."
    )
    alternatives: list[str] = Field(
        default_factory=list,
        description="Otras opciones tecnológicas evaluadas o descartadas antes de tomar la decisión final (ej. ['MongoDB', 'MySQL']).",
    )

class TechnicalIntegration(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        description="Nombre de la integración o del sistema objetivo con el que se conecta la solución (ej. 'Pasarela de Pagos Stripe')."
    )
    mechanism: str = Field(
        description="Mecanismo o protocolo técnico de comunicación (ej. 'REST API over HTTPS', 'gRPC', 'Webhooks', 'Kafka Event Stream')."
    )
    purpose: str = Field(
        description="Propósito técnico y funcional de la integración dentro del flujo general."
    )

class SecurityDesign(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    controls: list[str] = Field(
        default_factory=list,
        description="Lista de controles, protocolos y medidas de seguridad a implementar (ej. ['OAuth2 + JWT para autenticación', 'Cifrado en reposito AES-256', 'WAF para protección web']).",
    )

class ScalabilityDesign(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Lista de estrategias para escalar el sistema bajo alta demanda (ej. ['Auto-scaling horizontal en Kubernetes', 'Caché de lecturas con Redis', 'Particionamiento de BD']).",
    )

class AvailabilityDesign(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Medidas para garantizar el tiempo de actividad y tolerancia a fallos (ej. ['Despliegue Multi-AZ', 'Balanceador de carga con Health Checks', 'Backups automatizados cada 24h']).",
    )

class ObservabilityDesign(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Herramientas y mecanismos para monitoreo, métricas, logs y trazas (ej. ['Centralización de logs con Grafana Loki', 'OpenTelemetry para trazas distribuidas', 'Alertas PagerDuty']).",
    )

class DeploymentDesign(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Estrategias de CI/CD, infraestructura y despliegue (ej. ['Pipeline en GitHub Actions', 'Infraestructura como Código con Terraform', 'Estrategia Blue/Green deployment']).",
    )

class DataArchitecture(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    strategy: str = Field(
        description="Estrategia general para el diseño, almacenamiento, modelado y ciclo de vida de los datos (ej. 'Arquitectura Polyglot Persistence con PostgreSQL para transacciones y MongoDB para documentos')."
    )

class ServiceItem(BaseModel):
    """
    Representa un ítem de servicio o entregable dentro de la propuesta económica,
    incluyendo sus horas estimadas, tarifa y moneda.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    service_id: str = Field(
        description="Identificador único del servicio o componente (ej. 'SERV-001', 'DEV-FRONT')."
    )
    name: str = Field(
        description="Nombre descriptivo del servicio, módulo o entregable a realizar (ej. 'Desarrollo de API REST de Pagos')."
    )
    hours: Decimal = Field(
        description="Cantidad total de horas estimadas requeridas para completar este servicio específico."
    )
    hourly_rate: Decimal = Field(
        description="Tarifa por hora aplicable a este ítem de servicio en la moneda especificada."
    )
    currency: str = Field(
        default="USD",
        description="Código de moneda ISO 4217 correspondiente a la tarifa (ej. 'USD', 'PEN', 'EUR').",
    )

class EffortItem(BaseModel):
    """
    Representa el desglose de esfuerzo o tarea específica requerida dentro de un servicio o fase del proyecto.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    service_id: str = Field(
        description="Identificador del servicio o módulo al que pertenece este desglose de esfuerzo (ej. 'SERV-001')."
    )
    description: str = Field(
        description="Detalle o descripción específica de la tarea o actividad técnica a realizar (ej. 'Diseño e implementación de modelo de datos')."
    )
    hours: Decimal = Field(
        description="Cantidad de horas asociadas a esta tarea o actividad en particular."
    )