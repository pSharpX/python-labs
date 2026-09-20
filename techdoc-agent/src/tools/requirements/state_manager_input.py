from pydantic import BaseModel, Field

from src.shared.constants import Priority, Criticality, AnalysisStatus


class SaveMarkdownInput(BaseModel):
    content: str = Field(
        description="Contenido en formato Markdown que se guardará en el archivo."
    )
    filename: str = Field(
        description="Nombre del archivo Markdown que se creará, incluyendo la extensión .md."
    )

class UpdateContextInput(BaseModel):
    context: str = Field(
        description="Contexto funcional del analisis."
    )

class UpdateProblemNeedInput(BaseModel):
    problem_need: str = Field(
        description="Problema o necesidad funcional identificada."
    )

class AddObjectiveInput(BaseModel):
    objective: str = Field(
        description="El objetivo explícitamente identificado."
    )

class AddExpectedResultInput(BaseModel):
    expected_result: str = Field(
        description="El resultado esperado explícitamente identificado."
    )

class UpdateFunctionalRequirementInput(BaseModel):
    requirement_id: str = Field(
        description="Identificador del requisito funcional."
    )

    description: str = Field(
        description="Descripción actual del requisito funcional."
    )

    priority: Priority = Field(
        description="Prioridad del requisito."
    )

    actor: str | None = Field(
        default=None,
        description="Actor asociado al requisito."
    )

    process: str | None = Field(
        default=None,
        description="Proceso de negocio asociado al requisito."
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Criterios de aceptación proporcionados o confirmados explícitamente."
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Dependencias conocidas."
    )

    source: str | None = Field(
        default=None,
        description="Fuente del requisito."
    )

    confirmed: bool = Field(
        default=False,
        description="Indica si el requisito ha sido confirmado."
    )

class UpdateNonFunctionalRequirementInput(BaseModel):
    requirement_id: str = Field(
        description="Identificador del requisito no funcional."
    )

    category: str = Field(
        description="Categoria actual del requisito no funcional."
    )

    description: str = Field(
        description="Descripción actual del requisito no funcional."
    )

    priority: Priority = Field(
        description="Prioridad del requisito."
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Criterios de aceptación proporcionados o confirmados explícitamente."
    )

    source: str | None = Field(
        default=None,
        description="Fuente del requisito."
    )

    confirmed: bool = Field(
        default=False,
        description="Indica si el requisito ha sido confirmado."
    )

class AddAssumptionInput(BaseModel):
    description: str = Field(
        description="Descripción del supuesto identificado."
    )

class AddMissingInformationInput(BaseModel):
    description: str = Field(
        description="Descripción de la información faltante."
    )

    criticality: Criticality = Field(
        description="Nivel de criticidad de la información."
    )

    reason: str | None = Field(
        default=None,
        description="Razón por la que la información es necesaria."
    )

class AddClientQuestionInput(BaseModel):
    question: str = Field(
        description="Pregunta concreta para el cliente."
    )

    reason: str = Field(
        description="Razón de la pregunta."
    )

    related_to: str | None = Field(
        default=None,
        description="Requerimiento, proceso o elemento relacionado."
    )

class AddActorInput(BaseModel):
    name: str = Field(
        description="Nombre del actor."
    )

    actor_type: str = Field(
        description="Tipo de actor: usuario, área, sistema o tercero."
    )

    responsibility: str = Field(
        description="Responsabilidad del actor."
    )

class AddProcessInput(BaseModel):
    name: str = Field(
        description="Nombre del proceso."
    )

    objective: str = Field(
        description="Objetivo del proceso."
    )

    actors: list[str] = Field(
        default_factory=list,
        description="Actores involucrados."
    )

    main_flow: list[str] = Field(
        default_factory=list,
        description="Flujo principal conocido."
    )

    exceptions: list[str] = Field(
        default_factory=list,
        description="Excepciones conocidas."
    )

    result: str | None = Field(
        default=None,
        description="Resultado del proceso."
    )

class UpdateScopeInput(BaseModel):
    included: list[str] = Field(
        default_factory=list,
        description="Elementos incluidos."
    )

    excluded: list[str] = Field(
        default_factory=list,
        description="Elementos excluidos."
    )

    to_confirm: list[str] = Field(
        default_factory=list,
        description="Elementos pendientes de confirmación."
    )

class AddIntegrationInput(BaseModel):
    system: str = Field(
        description="Sistema involucrado."
    )

    purpose: str = Field(
        description="Propósito funcional de la integración."
    )

    data: list[str] = Field(
        default_factory=list,
        description="Datos intercambiados."
    )

    direction: str | None = Field(
        default=None,
        description="Dirección del intercambio."
    )

    frequency: str | None = Field(
        default=None,
        description="Frecuencia conocida."
    )

    status: str = Field(
        default="To Be Defined",
        description="Estado de definición."
    )

class AddFunctionalRiskInput(BaseModel):
    description: str = Field(
        description="Descripción del riesgo."
    )

    impact: str = Field(
        description="Impacto funcional."
    )

    cause: str = Field(
        description="Causa conocida."
    )

    action_or_validation: str | None = Field(
        default=None,
        description="Acción o validación requerida."
    )

class AddBusinessRuleInput(BaseModel):
    rule: str = Field(
        description="La regla de negocio a registrar."
    )

class AddDependencyInput(BaseModel):
    dependency: str = Field(
        description="La dependencia funcional a registrar."
    )

class AddConstraintInput(BaseModel):
    constraint: str = Field(
        description="La restricción funcional a registrar."
    )

class AddDataVolumetricInput(BaseModel):
    information: str = Field(
        description="La información sobre datos, cantidades, frecuencias o volumetrías."
    )

class UpdateAnalysisStatusInput(BaseModel):
    status: AnalysisStatus = Field(
        description="El estado general del análisis funcional a establecer."
    )

class GetAnalysisStatusInput(BaseModel):
    include_details: bool = Field(
        default=False,
        description="Incluir detalles de elementos pendientes."
    )