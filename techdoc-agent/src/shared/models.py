from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Literal, List, Optional, Self, ClassVar

from pydantic import Field, BaseModel, model_validator, ConfigDict

from src.utils.hashing import utcnow
from .enums import UserAction, ApprovalStatus, ApprovalDecision, ArtifactType, RequirementStatus, TechnicalStatus, \
    Confidence, EstimateStatus
from .constants import Priority, ServiceCategory


class WorkflowStatus(str, Enum):
    RUNNING = "running"
    AWAITING_USER = "awaiting_user"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    FAILED = "failed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
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
    model_config = ConfigDict(extra="ignore")

    id: str = Field(
        description="Identificador único del requerimiento (ej. 'RF-001')."
    )
    description: str = Field(
        description="Descripción clara, concisa y orientada a la acción de lo que el sistema debe hacer."
    )
    priority: Priority = Field(
        default="must",
        description="Nivel de prioridad o urgencia del requerimiento para el proyecto (i.e 'must', 'should', 'could').",
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
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

    topic: str = Field(
        description="Tema de la información no proporcionada o vacíos conceptuales detectados."
    )
    criticality: Literal["critical", "important", "desirable"] = Field(
        description="Nivel de criticidad del vacío de información para la estimación y diseño arquitectónico."
    )
    reason: str | None = Field(
        default=None,
        description="Explicación de por qué esta información faltante afecta la fase actual de la propuesta.",
    )
    blocking: bool = Field(description="Verdadero cuando la arquitectura o la estimación no pueden continuar sin esto")

class ClientQuestion(BaseModel):
    model_config = ConfigDict(extra="ignore")

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
    model_config = ConfigDict(extra="ignore")

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

class Stakeholder(BaseModel):
    name: str = Field(description="Role or person")
    interest: str = ""

class DataVolumetrics(BaseModel):
    data_sources: list[str] = Field(default_factory=list)
    data_volumes: str = Field(default="", description="e.g. '2M records, 50 GB'; empty when unknown")
    transaction_volumes: str = Field(default="", description="e.g. '10k orders/day'; empty when unknown")
    growth_expectations: str = ""

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
    service_category: str = Field(
        default="default",
        description="Categoría general del servicio solicitado que se utiliza para seleccionar las reglas de validación "
                    "(p. ej., integration, data_platform, application_development, cloud_migration, ai_solution, default)",
    )
    customer_name: str = ""

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
    stakeholders: list[Stakeholder] = Field(default_factory=list)

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

    data_and_volumetrics: DataVolumetrics = Field(
        default_factory=DataVolumetrics,
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

    client_questions: list[str] = Field(
        default_factory=list,
        description=(
            "Preguntas que deben realizarse al cliente para aclarar "
            "ambigüedades, validar supuestos, completar información faltante "
            "o tomar decisiones necesarias para continuar con el análisis."
        ),
    )
    ready_for_architecture: bool = Field(
        default=False,
        description="Indica si la información proporcionada es suficiente y clara para proceder al diseño de la arquitectura técnica.",
    )

    readiness_reason: str = Field(
        default="",
        description="Justificación detallada de por qué el proyecto está o no está listo para continuar a la fase de arquitectura técnica.",
    )
    final_brief: str = Field(default="", description="Breve resumen para el arquitecto; se completa cuando está listo")
    change_summary: str = Field(default="", description="Cambios respecto a la versión anterior, si los hay")

class RequirementsSpecification(Requirements):
    proposal_id: str
    version: int = 1
    status: RequirementStatus = RequirementStatus.IN_PROGRESS
    waiting_for_customer: bool = False
    validation_issues: list[str] = Field(default_factory=list)

    # Fields excluded when fingerprinting (metadata, not content)
    FINGERPRINT_EXCLUDE: ClassVar[tuple[str, ...]] = (
        "proposal_id",
        "version",
        "status",
        "waiting_for_customer",
        "validation_issues",
        "client_questions",
        "analyst_assessment_ready",
        "change_summary",
    )

class Architecture(BaseModel):
    """
    Representa el estilo arquitectónico general, la síntesis del diseño de software
    y su representación gráfica en código Mermaid.
    """

    model_config = ConfigDict(
        extra="ignore",
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

class CustomerSegment(str, Enum):
    SMB = "SMB"
    CORPORATE = "Corporate"

class CatalogItem(BaseModel):
    """Producto o servicio seleccionado del catálogo comercial."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(
        description=(
            "Nombre exacto del producto o servicio devuelto por "
            "la herramienta obtener_catalogo_por_familias."
        )
    )
    justification: str = Field(
        description=(
            "Justificación de la selección en función de los "
            "requerimientos del cliente."
        )
    )

class ServiceClassification(BaseModel):
    """
    Resultados del análisis de clasificación comercial del requerimiento.
    """

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    business_line: str = Field(
        description="Línea de negocio seleccionada entre las opciones devueltas por la herramienta correspondiente."
    )
    segmentation: CustomerSegment = Field(
        description=(
            "Segmento seleccionado según los criterios devueltos "
            "por obtener_criterio_segmentacion. Solo SMB o Corporate."
        )
    )
    catalog_items: list[CatalogItem] = Field(
        min_length=1,
        description=(
            "Productos y servicios seleccionados exclusivamente "
            "del catálogo devuelto para la línea de negocio elegida."
        )
    )
    classification_rationale: str = Field(
        description=(
            "Resumen conciso que justifica la segmentación, "
            "la línea de negocio y la selección del catálogo."
        )
    )

class ProjectPhase(BaseModel):
    """
    Fase estructurada del proyecto con sus actividades y entregables clave.
    """

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

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

class RequiredProfile(BaseModel):
    """
    Perfil técnico o funcional requerido para el proyecto, consultado desde el catálogo.
    """

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    role_id: str
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

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    total_duration_weeks: Decimal = Field(
        description="Duración total estimada del proyecto expresada en semanas."
    )
    # total_effort_hours: Decimal | None = Field(
    #     default=None,
    #     description="Esfuerzo total estimado expresado en horas de trabajo."
    # )
    summary: str = Field(
        description="Resumen o descripción del cronograma de alto nivel y sus hitos principales."
    )

class DocumentationSource(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
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
        extra="ignore",
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
        extra="ignore",
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
        extra="ignore",
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
        extra="ignore",
        str_strip_whitespace=True,
    )

    controls: list[str] = Field(
        default_factory=list,
        description="Lista de controles, protocolos y medidas de seguridad a implementar (ej. ['OAuth2 + JWT para autenticación', 'Cifrado en reposito AES-256', 'WAF para protección web']).",
    )

class ScalabilityDesign(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Lista de estrategias para escalar el sistema bajo alta demanda (ej. ['Auto-scaling horizontal en Kubernetes', 'Caché de lecturas con Redis', 'Particionamiento de BD']).",
    )

class AvailabilityDesign(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Medidas para garantizar el tiempo de actividad y tolerancia a fallos (ej. ['Despliegue Multi-AZ', 'Balanceador de carga con Health Checks', 'Backups automatizados cada 24h']).",
    )

class ObservabilityDesign(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Herramientas y mecanismos para monitoreo, métricas, logs y trazas (ej. ['Centralización de logs con Grafana Loki', 'OpenTelemetry para trazas distribuidas', 'Alertas PagerDuty']).",
    )

class DeploymentDesign(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    strategy: list[str] = Field(
        default_factory=list,
        description="Estrategias de CI/CD, infraestructura y despliegue (ej. ['Pipeline en GitHub Actions', 'Infraestructura como Código con Terraform', 'Estrategia Blue/Green deployment']).",
    )

class DataArchitecture(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    strategy: str = Field(
        description="Estrategia general para el diseño, almacenamiento, modelado y ciclo de vida de los datos (ej. 'Arquitectura Polyglot Persistence con PostgreSQL para transacciones y MongoDB para documentos')."
    )

class OpenQuestion(BaseModel):
    question: str = Field(
        description="Pregunta abierta, duda técnica o ambigüedad pendiente de resolver con los stakeholders o el equipo de arquitectura."
    )
    blocking: bool = Field(
        default=False,
        description="Indica si la pregunta representa un bloqueador crítico que impide avanzar con el diseño detallado, la estimación o la ejecución."
    )

class ImplementationPhase(BaseModel):
    id: str = Field(
        description="Identificador único de la fase de implementación (e.g., 'PH-1')."
    )
    name: str = Field(
        description="Nombre descriptivo de la fase dentro de la hoja de ruta de implementación."
    )
    objective: str = Field(
        default="",
        description="Meta o propósito principal que se busca alcanzar al finalizar esta fase."
    )
    order: int = Field(
        description="Número secuencial que define el orden de ejecución de la fase en el cronograma."
    )
    duration_weeks: float = Field(
        ge=0,
        description="Duración estimada de la fase expresada en semanas."
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="Lista de IDs de otras fases que deben completarse o iniciarse antes de poder arrancar esta fase (dependencias de prelación)."
    )

class PhaseActivity(BaseModel):
    id: str = Field(
        description="Identificador único de la actividad (e.g., 'ACT-1.1')."
    )
    phase_id: str = Field(
        description="Identificador de la fase (`ImplementationPhase`) a la cual pertenece esta actividad."
    )
    name: str = Field(
        description="Nombre o título de la actividad a realizar."
    )
    description: str = Field(
        default="",
        description="Detalle o alcance de lo que comprende la ejecución de esta actividad."
    )
    tasks: list[str] = Field(
        default_factory=list,
        description="Lista de tareas técnicas o operativas específicas requeridas para completar la actividad."
    )
    profile_ids: list[str] = Field(
        default_factory=list,
        description="IDs correspondientes a los perfiles profesionales requeridos para ejecutar la actividad (provenientes de la función `obtener_perfiles`)."
    )
    deliverable_ids: list[str] = Field(
        default_factory=list,
        description="Lista de IDs de los entregables o productos esperados como resultado de la ejecución de esta actividad."
    )

class Deliverable(BaseModel):
    id: str = Field(
        description="Identificador único del entregable (e.g., 'DEL-1')."
    )
    phase_id: str = Field(
        description="Identificador de la fase (`ImplementationPhase`) a la cual está asociado este entregable."
    )
    name: str = Field(
        description="Nombre o título del entregable (e.g., 'Documento de Arquitectura Base', 'Diagrama de Despliegue')."
    )
    description: str = Field(
        default="",
        description="Descripción detallada del contenido, formato o criterios de aceptación del entregable esperado."
    )

class AcceptanceCriterion(BaseModel):
    deliverable_id: str
    description: str

class Milestone(BaseModel):
    name: str = Field(
        description="Nombre o título del hito clave o punto de control (e.g., 'Aprobación de Arquitectura de Seguridad', 'Go-Live Fase 1')."
    )
    phase_id: str = Field(
        description="Identificador de la fase (`ImplementationPhase`) a la cual está vinculado o en la que concluye este hito."
    )
    target_week: float = Field(
        ge=0,
        description="Semana proyectada en el cronograma en la que se debe alcanzar o cumplir este hito."
    )

class TraceabilityLink(BaseModel):
    requirement_id: str
    covered_by: list[str] = Field(default_factory=list, description="Activity/component/deliverable ids")
    notes: str = ""

class RiskMitigation(BaseModel):
    category: str = Field(description="architectural | technical | operational | security | delivery")
    description: str
    probability: str = "medium"
    impact: str = "medium"
    mitigation: str

class TechnicalDesignContent(BaseModel):
    """Fields authored by the architect LLM (structured output schema)."""

    executive_summary: str = ""
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
    integrations: list[Integration] = Field(
        default_factory=list,
        description="Detalle de las integraciones técnicas con sistemas internos, externos o APIs de terceros.",
    )
    milestones: list[Milestone] = Field(default_factory=list)
    requirements_traceability: list[TraceabilityLink] = Field(default_factory=list)
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
    assumptions: list[Assumption] = Field(
        default_factory=list,
        description="Supuestos y premisas técnicas consideradas verdaderas para fundamentar este diseño arquitectónico.",
    )
    constraints: list[str] = Field(default_factory=list)
    # 8. Prerequisites
    prerequisites: list[str] = Field(
        default_factory=list,
        description="Condiciones, insumos o accesos previos que deben cumplirse antes de iniciar el trabajo.",
    )
    dependencies: list[str] = Field(default_factory=list)
    technical_risks: list[RiskMitigation] = Field(
        default_factory=list,
        description="Riesgos técnicos identificados que podrían impactar el desarrollo o la operación, junto a sus mitigaciones.",
    )
    scope: list[str] = Field(
        default_factory=list,
        description="Lista de funcionalidades, componentes, sistemas o requerimientos incluidos formalmente dentro del alcance del diseño de arquitectura."
    )
    out_of_scope: list[str] = Field(
        default_factory=list,
        description="Lista de elementos, tecnologías, casos de uso o fases que quedan explícitamente excluidos para gestionar expectativas y prevenir desviaciones (scope creep)."
    )
    documentation_sources: list[DocumentationSource] = Field(
        default_factory=list,
        description="Referencias o fuentes de documentación utilizadas o requeridas para este diseño.",
    )
    # 1. Service Classification & Identification
    requested_service: ServiceClassification = Field(
        description="Clasificación comercial del requerimiento según los resultados de las herramientas de segmentación, líneas de negocio y catálogo."
    )

    # 2, 3 & 4. Solution Phasing, Activity Mapping & Deliverables
    implementation_phases: list[ImplementationPhase] = Field(
        default_factory=list,
        description="Fases estructuradas del proyecto, incluyendo actividades asociadas y entregables concretos por fase.",
    )
    phase_activities: list[PhaseActivity] = Field(default_factory=list)
    deliverables: list[Deliverable] = Field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)

    # 5. Resource & Profile Identification
    required_profiles: list[RequiredProfile] = Field(
        default_factory=list,
        description="Perfiles técnicos y funcionales requeridos obtenidos según la regla de dependencia del catálogo.",
    )
    # 6. Project Timeline Estimation
    timeline_estimation: TimelineEstimation = Field(
        description="Estimación global de duración (semanas) y esfuerzo total (horas) para la ejecución del proyecto."
    )
    open_questions: list[OpenQuestion] = Field(default_factory=list)

class TechnicalProposal(TechnicalDesignContent):
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

    proposal_id: str
    version: int = 1
    status: TechnicalStatus = TechnicalStatus.READY
    based_on_requirements_fingerprint: str
    based_on_requirements_version: int

    validation_issues: list[str] = Field(default_factory=list)

    FINGERPRINT_EXCLUDE: ClassVar[tuple[str, ...]] = ("proposal_id", "version", "status", "validation_issues")

class ServiceItem(BaseModel):
    """
    Representa un ítem de servicio o entregable dentro de la propuesta económica,
    incluyendo sus horas estimadas, tarifa y moneda.
    """

    model_config = ConfigDict(
        extra="ignore",
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
        extra="ignore",
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

class EffortItemDraft(BaseModel):
    activity_id: str = Field(description="ID de la actividad de la propuesta técnica")
    profile_id: str = Field(description="ID del perfil autorizado de la propuesta técnica")
    hours: float = Field(description="Esfuerzo estimado en horas para este perfil en esta actividad")
    rationale: str = ""
    confidence: Confidence = Confidence.MEDIUM

class EffortMappingDraft(BaseModel):
    items: list[EffortItemDraft]
    estimation_method: str = Field(default="Bottom-up effort per activity and profile")
    commercial_assumptions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    confidence_level: Confidence = Confidence.MEDIUM
    missing_information: list[str] = Field(default_factory=list)
    scope_change_detected: bool = Field(
        default=False,
        description="Verdadero si los comentarios del usuario cambian el alcance o los requerimientos técnicos y no solo el esfuerzo",
    )
    explanation: str = Field(default="", description="Explicación breve de la estimación para el usuario")


# ---- Configured rules ---------------------------------------------------------------

class RateCard(BaseModel):
    currency: str
    rates: dict[str, Decimal] = Field(description="profile_id -> hourly rate")
    source: str = ""
    effective_date: str = ""


class PercentageRule(BaseModel):
    enabled: bool = False
    rate: Decimal = Decimal("0")
    label: str = ""


class RoundingRule(BaseModel):
    quantum: Decimal = Decimal("0.01")
    mode: str = Field(default="ROUND_HALF_UP", description="Any decimal rounding mode name")
    hours_quantum: Decimal = Decimal("0.5")


class FinancialRules(BaseModel):
    currency: str
    contingency: PercentageRule = Field(default_factory=PercentageRule)
    discount: PercentageRule = Field(default_factory=PercentageRule)
    tax: PercentageRule = Field(default_factory=PercentageRule)
    rounding: RoundingRule = Field(default_factory=RoundingRule)
    max_hours_per_item: Decimal = Decimal("2000")
    require_all_activities_estimated: bool = True
    formula_description: str = (
        "line_amount = hours × hourly_rate; subtotal = Σ line_amount; "
        "contingency = subtotal × contingency_rate (if enabled); "
        "discount = (subtotal + contingency) × discount_rate (if enabled); "
        "taxable_base = subtotal + contingency − discount; taxes = taxable_base × tax_rate (if enabled); "
        "total = taxable_base + taxes"
    )

# ---- Computed estimate -------------------------------------------------------------


class EstimateLineItem(BaseModel):
    phase_id: str
    phase_name: str
    activity_id: str
    activity_name: str
    profile_id: str
    profile_name: str
    hours: Decimal
    hourly_rate: Decimal
    amount: Decimal
    rationale: str = ""
    confidence: Confidence = Confidence.MEDIUM


class ProfileEstimate(BaseModel):
    profile_id: str
    profile_name: str
    hours: Decimal
    hourly_rate: Decimal
    amount: Decimal


class PhaseEstimate(BaseModel):
    phase_id: str
    phase_name: str
    hours: Decimal
    amount: Decimal


class AdjustmentLine(BaseModel):
    label: str
    rate: Decimal
    base: Decimal
    amount: Decimal
    applied: bool


class FinancialEstimate(BaseModel):
    """
    Esquema de salida estructurada para la estimación financiera y desglose de costos
    de la propuesta comercial / técnica.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    proposal_id: str
    version: int = 1
    status: EstimateStatus = EstimateStatus.READY_FOR_APPROVAL
    based_on_technical_fingerprint: str
    based_on_technical_version: int
    based_on_requirements_fingerprint: str

    currency: str
    estimation_method: str
    formula: str
    rate_card_source: str = ""
    activity_estimates: list[EstimateLineItem] = Field(default_factory=list)
    profile_estimates: list[ProfileEstimate] = Field(default_factory=list)
    phase_estimates: list[PhaseEstimate] = Field(default_factory=list)
    hours_by_profile: dict[str, Decimal] = Field(default_factory=dict)
    total_hours: Decimal = Decimal("0")
    subtotal: Decimal = Decimal("0")
    contingency: AdjustmentLine | None = None
    discount: AdjustmentLine | None = None
    taxes: AdjustmentLine | None = None
    total_cost: Decimal = Decimal("0")
    estimated_duration: str = ""
    commercial_assumptions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    confidence_level: Confidence = Confidence.MEDIUM
    explanation: str = ""
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUESTED
    approval_feedback: str | None = None
    revision_feedback: str | None = Field(default=None, description="Feedback this version responded to")

    FINGERPRINT_EXCLUDE: ClassVar[tuple[str, ...]] = (
        "proposal_id",
        "version",
        "status",
        "approval_status",
        "approval_feedback",
    )


class ApprovalRecord(BaseModel):
    decision: ApprovalDecision
    status: ApprovalStatus
    estimate_version: int
    estimate_fingerprint: str
    technical_version: int
    technical_fingerprint: str
    requirements_fingerprint: str
    user_id: str
    feedback: str | None = None
    decided_at: datetime = Field(default_factory=utcnow)

class NarrativeDraft(BaseModel):
    """Explanatory prose authored by the LLM from approved data. Contains no new facts."""

    proposal_title: str = Field(description="Short professional title for the proposal")
    executive_summary: str
    context_introduction: str = ""
    solution_introduction: str = ""
    delivery_introduction: str = ""
    financial_introduction: str = Field(default="", description="Must not restate or alter any figure")
    closing_statement: str = ""

class DocumentMetadata(BaseModel):
    proposal_id: str
    document_version: int
    filename: str
    file_path: str = Field(description="Path relative to the configured output directory (never absolute)")
    created_at: datetime
    approval_status: ApprovalStatus
    content_hash: str
    requirements_version: int
    technical_version: int
    estimate_version: int
    estimate_fingerprint: str

class ChatTurn(BaseModel):
    role: str = Field(description="user | assistant | system")
    content: str
    timestamp: datetime = Field(default_factory=utcnow)

class ArtifactVersionInfo(BaseModel):
    artifact_type: ArtifactType
    version: int
    fingerprint: str
    based_on: dict[str, str] = Field(default_factory=dict, description="upstream artifact type -> fingerprint")
    created_at: datetime = Field(default_factory=utcnow)

