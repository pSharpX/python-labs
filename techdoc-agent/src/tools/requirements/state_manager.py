from pathlib import Path
from typing import Type

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from pydantic import BaseModel

from src.shared import Priority
from src.state import NonFunctionalRequirement, Requirement, Assumption, MissingInformation, ClientQuestion, Actor, \
    Process, ProposalScope, Integration, Risk
from src.state.requirements import RequirementsState
from .state_manager_input import SaveMarkdownInput, UpdateFunctionalRequirementInput, AddAssumptionInput, \
    AddMissingInformationInput, AddClientQuestionInput, AddActorInput, AddProcessInput, UpdateScopeInput, \
    AddIntegrationInput, AddFunctionalRiskInput, GetAnalysisStatusInput, UpdateNonFunctionalRequirementInput, \
    UpdateContextInput, UpdateProblemNeedInput, AddBusinessRuleInput, AddDependencyInput, AddConstraintInput, \
    AddDataVolumetricInput, AddObjectiveInput, AddExpectedResultInput, UpdateAnalysisStatusInput


class SaveMarkdownTool(BaseTool):
    name: str = "save_markdown"
    description: str = (
        "Crea un archivo Markdown y guarda en él el contenido proporcionado. "
        "Utiliza esta herramienta cuando el usuario solicite guardar, exportar "
        "o persistir contenido en formato Markdown como un archivo local .md."
    )
    args_schema: Type[BaseModel] = SaveMarkdownInput

    output_dir: str = "../../../docs/outcomes"

    def _run(self, content: str, filename: str) -> str:
        output_path = Path(self.output_dir) / filename

        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure the file has a .md extension
        if output_path.suffix.lower() != ".md":
            output_path = output_path.with_suffix(".md")

        output_path.write_text(content, encoding="utf-8")

        return f"Markdown file successfully saved to: {output_path}"

    async def _arun(self, content: str, filename: str) -> str:
        return self._run(content, filename)

@tool("actualizar_contexto", args_schema=UpdateContextInput)
def update_context(
    context: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Actualiza el contexto funcional del análisis.
    Usar cuando exista información confirmada sobre la situación actual, motivación o contexto del cliente.
    """

    return Command(
        update={
            "context": context,
            "messages": [
                ToolMessage(
                    content=f"Contexto actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("actualizar_problema_necesidad", args_schema=UpdateProblemNeedInput)
def update_problem_need(
    problem_need: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Actualiza el problema o necesidad funcional identificada.
    Solo debe utilizarse cuando la información esté sustentada por el cliente o por información explícitamente proporcionada.
    """

    return Command(
        update={
            "problem_need": problem_need,
            "messages": [
                ToolMessage(
                    content=f"Problema y/o necesidad actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_objetivo", args_schema=AddObjectiveInput)
def add_objective(
    objective: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Agrega un objetivo explícitamente identificado en la solicitud del cliente. No agregues objetivos inferidos.
    """

    return Command(
        update={
            "objectives": [objective],
            "messages": [
                ToolMessage(
                    content="Objetivo actualizado correctamente.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_resultado_esperado", args_schema=AddExpectedResultInput)
def add_expected_result(
    expected_result: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Agrega un resultado esperado explícitamente identificado en la solicitud del cliente.
    """

    return Command(
        update={
            "expected_results": [expected_result],
            "messages": [
                ToolMessage(
                    content="Resultado actualizado correctamente.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("actualizar_estado_analisis", args_schema=UpdateAnalysisStatusInput)
def update_analysis_status(
    status: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Actualiza el estado general del análisis funcional.
    Usa 'analyzing' mientras el análisis está en progreso, 'awaiting_client_information' cuando existe información crítica pendiente del cliente, y 'ready_for_architecture' únicamente cuando el análisis funcional está suficientemente completo.
    """

    return Command(
        update={
            "status": status,
            "messages": [
                ToolMessage(
                    content=f"Estado actualizado a '{status}'.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_regla_negocio", args_schema=AddBusinessRuleInput)
def add_business_rule(
    rule: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Registra una regla de negocio identificada explícitamente.
    """

    return Command(
        update={
            "business_rules": [rule],
            "messages": [
                ToolMessage(
                    content="Regla de negocio actualizado correctamente.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_dependencia", args_schema=AddDependencyInput)
def add_dependency(
    dependency: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Registra una dependencia funcional identificada en el análisis.
    """

    return Command(
        update={
            "dependencies": [dependency],
            "messages": [
                ToolMessage(
                    content="Dependencia actualizado correctamente.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_restriccion", args_schema=AddConstraintInput)
def add_constraint(
    constraint: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Registra una restricción funcional explícitamente identificada.
    """

    return Command(
        update={
            "constraints": [constraint],
            "messages": [
                ToolMessage(
                    content="Restricción actualizado correctamente.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_dato_volumetria", args_schema=AddDataVolumetricInput)
def add_data_volumetric(
    information: str,
    runtime: ToolRuntime,
) -> Command:
    """
    Registra información conocida sobre datos, cantidades, frecuencias o volumetrías.
    """

    return Command(
        update={
            "data_and_volumetrics": [information],
            "messages": [
                ToolMessage(
                    content="Información de datos o volumetría actualizado correctamente.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("actualizar_requerimiento_no_funcional", args_schema=UpdateNonFunctionalRequirementInput)
def update_non_functional_requirement(
    runtime: ToolRuntime[RequirementsState],
    requirement_id: str,
    category: str,
    description: str,
    priority: Priority,
    acceptance_criteria: list[str] | None = None,
    source: str | None = None,
    confirmed: bool = False,
) -> Command:
    """
    Actualiza un requerimiento no funcional identificado durante el análisis.
    Utilizar para crear o modificar un requerimiento no funcional sin inventar información.
    """

    return Command(
        update={
            "non_functional_requirements": [
                NonFunctionalRequirement(
                    id=requirement_id,
                    category=category,
                    description=description,
                    priority=priority,
                    acceptance_criteria=acceptance_criteria or [],
                    source=source,
                    confirmed=confirmed,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Requerimientos no funcionales actualizados correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("actualizar_requerimiento_funcional", args_schema=UpdateFunctionalRequirementInput)
def update_functional_requirement(
    runtime: ToolRuntime[RequirementsState],
    requirement_id: str,
    description: str,
    priority: Priority,
    actor: str | None = None,
    process: str | None = None,
    acceptance_criteria: list[str] | None = None,
    dependencies: list[str] | None = None,
    source: str | None = None,
    confirmed: bool = False,
) -> Command:
    """
    Actualiza un requerimiento funcional identificado durante el análisis. Utilizar para crear o modificar un requerimiento funcional sin inventar información.
    """

    return Command(
        update={
            "functional_requirements": [
                Requirement(
                    id=requirement_id,
                    description=description,
                    priority=priority,
                    actor=actor,
                    process=process,
                    acceptance_criteria=acceptance_criteria or [],
                    dependencies=dependencies or [],
                    source=source,
                    confirmed=confirmed,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Requerimientos funcionales actualizados correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_supuesto", args_schema=AddAssumptionInput)
def add_assumption(
    description: str,
    runtime: ToolRuntime[RequirementsState],
) -> Command:
    """
    Registra un supuesto identificado durante el análisis. Cualquier supuesto requiere validación del cliente.
    """

    return Command(
        update={
            "assumptions": [
                Assumption(
                    description=description,
                    requires_validation=True,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Supuesto actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_information_faltante", args_schema=AddMissingInformationInput)
def add_missing_information(
    runtime: ToolRuntime[RequirementsState],
    description: str,
    criticality: str,
    reason: str | None = None,
) -> Command:
    """
    Registra información faltante que debe ser validada con el cliente. No asumir valores no proporcionados.
    """

    return Command(
        update={
            "missing_information": [
                MissingInformation(
                    description=description,
                    criticality=criticality,
                    reason=reason,
                )
            ],
            "status": "awaiting_client_information",
            "messages": [
                ToolMessage(
                    content=f"Información faltante actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_pregunta_cliente", args_schema=AddClientQuestionInput)
def add_client_question(
    runtime: ToolRuntime[RequirementsState],
    question: str,
    reason: str,
    related_to: str | None = None,
) -> Command:
    """
    Registra una pregunta concreta para el cliente. Utilizar únicamente para resolver ambigüedades, confirmar alcance o completar información necesaria.
    """

    return Command(
        update={
            "client_questions": [
                ClientQuestion(
                    question=question,
                    reason=reason,
                    related_to=related_to,
                )
            ],
            #"status": "awaiting_client_information",
            "messages": [
                ToolMessage(
                    content=f"Preguntas para el cliente actualizados correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_actor", args_schema=AddActorInput)
def add_actor(
    name: str,
    actor_type: str,
    responsibility: str,
    runtime: ToolRuntime[RequirementsState],
):
    """
    Registra un actor identificado durante el análisis funcional. Solo utilizar información explícitamente proporcionada.
    """

    return Command(
        update={
            "actors": [
                Actor(
                    name=name,
                    type=actor_type,
                    responsibility=responsibility,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Actor actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_proceso", args_schema=AddProcessInput)
def add_process(
    runtime: ToolRuntime[RequirementsState],
    name: str,
    objective: str,
    actors: list[str],
    main_flow: list[str],
    exceptions: list[str],
    result: str | None = None,
):
    """
    Registra un proceso funcional identificado durante el análisis. No introducir pasos técnicos ni decisiones de arquitectura.
    """

    return Command(
        update={
            "processes": [
                Process(
                    name=name,
                    objective=objective,
                    actors=actors,
                    main_flow=main_flow,
                    exceptions=exceptions,
                    result=result,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Proceso actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_alcance_funcional", args_schema=UpdateScopeInput)
def update_scope(
    runtime: ToolRuntime[RequirementsState],
    included: list[str],
    excluded: list[str],
    to_confirm: list[str],
) -> Command:
    """
    Actualiza el alcance funcional separando elementos incluidos, excluidos y pendientes de confirmación.
    """

    return Command(
        update={
            "scope": ProposalScope(
                included=included,
                excluded=excluded,
                to_confirm=to_confirm,
            ),
            "messages": [
                ToolMessage(
                    content=f"Alcance funcional actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_integracion", args_schema=AddIntegrationInput)
def add_integration(
    runtime: ToolRuntime[RequirementsState],
    system: str,
    purpose: str,
    data: list[str],
    direction: str | None = None,
    frequency: str | None = None,
    status: str = "To Be Defined",
) -> Command:
    """
    Registra una integración funcional identificada. No seleccionar protocolos, tecnologías o servicios técnicos.
    """

    return Command(
        update={
            "integrations": [
                Integration(
                    system=system,
                    purpose=purpose,
                    data=data,
                    direction=direction,
                    frequency=frequency,
                    status=status,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Integración actualizado correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("agregar_riesgo_funcional", args_schema=AddFunctionalRiskInput)
def add_functional_risk(
    runtime: ToolRuntime[RequirementsState],
    description: str,
    impact: str,
    cause: str,
    action_or_validation: str | None = None,
) -> Command:
    """
    Registra un riesgo funcional relacionado con ambigüedades, dependencias, restricciones o vacíos.
    """

    return Command(
        update={
            "risks": [
                Risk(
                    description=description,
                    impact=impact,
                    cause=cause,
                    action_validation=action_or_validation,
                )
            ],
            "messages": [
                ToolMessage(
                    content=f"Riesgo funcionales actualizados correctamente",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool("obtener_estado_analisis_actual", args_schema=GetAnalysisStatusInput)
def get_analysis_status(
    runtime: ToolRuntime[RequirementsState],
    include_details: bool = False,
) -> str:
    """
    Obtiene el estado actual del análisis funcional, incluyendo requisitos, información faltante y preguntas abiertas.
    """

    state = runtime.state
    result = {
        "requirements": len(
            state.get(
                "functional_requirements",
                [],
            )
        ),
        "non_functional_requirements": len(
            state.get(
                "non_functional_requirements",
                [],
            )
        ),
        "actors": len(
            state.get("actors", [])
        ),
        "processes": len(
            state.get("processes", [])
        ),
        "integrations": len(
            state.get("integrations", [])
        ),
        "missing_information": len(
            state.get(
                "missing_information",
                [],
            )
        ),
        "client_questions": len(
            state.get(
                "client_questions",
                [],
            )
        ),
        "assumptions": len(
            state.get("assumptions", [])
        ),
        "risks": len(
            state.get("risks", [])
        ),
        "status": state.get("status", "analyzing"),
    }

    if include_details:
        result["missing_information_details"] = [
            item.model_dump()
            for item in state.get(
                "missing_information",
                [],
            )
        ]

        result["client_questions_details"] = [
            item.model_dump()
            for item in state.get(
                "client_questions",
                [],
            )
        ]

    return str(result)