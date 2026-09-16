from pathlib import Path
from typing import Type

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from pydantic import BaseModel

from state import TechDocReqScoutState, Priority, Requirement, Assumption, MissingInformation, ClientQuestion, Actor, \
    Process, Integration, Risk, ProposalScope
from tools_input import SaveMarkdownInput, UpdateFunctionalRequirementInput, AddAssumptionInput, \
    AddMissingInformationInput, AddClientQuestionInput, AddActorInput, AddProcessInput, UpdateScopeInput, \
    AddIntegrationInput, AddFunctionalRiskInput, GetAnalysisStatusInput


class SaveMarkdownTool(BaseTool):
    name: str = "save_markdown"
    description: str = (
        "Crea un archivo Markdown y guarda en él el contenido proporcionado. "
        "Utiliza esta herramienta cuando el usuario solicite guardar, exportar "
        "o persistir contenido en formato Markdown como un archivo local .md."
    )
    args_schema: Type[BaseModel] = SaveMarkdownInput

    output_dir: str = "./docs/outcomes"

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


@tool(args_schema=UpdateFunctionalRequirementInput)
def update_functional_requirement(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Functional requirements updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddAssumptionInput)
def add_assumption(
    description: str,
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Assumptions updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddMissingInformationInput)
def add_missing_information(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Missing Information updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddClientQuestionInput)
def add_client_question(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Client Questions updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddActorInput)
def add_actor(
    name: str,
    actor_type: str,
    responsibility: str,
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Actors updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddProcessInput)
def add_process(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Processes updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=UpdateScopeInput)
def update_scope(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Scope updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddIntegrationInput)
def add_integration(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Integrations updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=AddFunctionalRiskInput)
def add_functional_risk(
    runtime: ToolRuntime[TechDocReqScoutState],
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
                    content=f"Functional risk updated successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool(args_schema=GetAnalysisStatusInput)
def get_analysis_status(
    runtime: ToolRuntime[TechDocReqScoutState],
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