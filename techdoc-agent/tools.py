
from abc import ABC
from pathlib import Path
from typing import TypeVar, Type

from langchain_core.tools import BaseTool, ToolException
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from pydantic import BaseModel

from state import TechDocReqScoutState, Priority, Requirement, Assumption, MissingInformation, ClientQuestion, Actor, \
    Process, Integration, Risk, ProposalScope
from tools_input import SaveMarkdownInput, UpdateFunctionalRequirementInput, AddAssumptionInput, \
    AddMissingInformationInput, Criticality, AddClientQuestionInput, AddActorInput, AddProcessInput, UpdateScopeInput, \
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


StateT = TypeVar("StateT")

class StateMutationTool(BaseTool, ABC):
    """
    Base class for tools that mutate LangGraph agent state.
    """

    def _validate_runtime(
        self,
        runtime: ToolRuntime | None,
    ) -> ToolRuntime:
        if runtime is None:
            raise ToolException(
                "Runtime is required for state mutation."
            )

        return runtime


class UpdateFunctionalRequirementTool(
    StateMutationTool
):
    name: str = "update_functional_requirement"
    description: str = (
        "Actualiza un requerimiento funcional identificado durante "
        "el análisis. Utilizar para crear o modificar un requerimiento "
        "funcional sin inventar información."
    )

    args_schema: type[BaseModel] = UpdateFunctionalRequirementInput

    def _run(
        self,
        requirement_id: str,
        description: str,
        priority: Priority,
        actor: str | None = None,
        process: str | None = None,
        acceptance_criteria: list[str] | None = None,
        dependencies: list[str] | None = None,
        source: str | None = None,
        confirmed: bool = False,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        requirement = Requirement(
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

        current = list(
            runtime.state.get(
                "functional_requirements",
                [],
            )
        )

        replaced = False

        for index, existing in enumerate(current):
            if existing.id == requirement_id:
                current[index] = requirement
                replaced = True
                break

        if not replaced:
            current.append(requirement)

        return Command(
            update={
                "functional_requirements": current,
            }
        )

    async def _arun(
        self,
        requirement_id: str,
        description: str,
        priority: Priority,
        actor: str | None = None,
        process: str | None = None,
        acceptance_criteria: list[str] | None = None,
        dependencies: list[str] | None = None,
        source: str | None = None,
        confirmed: bool = False,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(
            requirement_id,
            description,
            priority,
            actor,
            process,
            acceptance_criteria,
            dependencies,
            source,
            confirmed,
            runtime
        )


class AddAssumptionTool(
    StateMutationTool
):
    name: str = "add_assumption"
    description: str = (
        "Registra un supuesto identificado durante el análisis. "
        "Todo supuesto requiere validación del cliente."
    )

    args_schema: type[BaseModel] = AddAssumptionInput

    def _run(
        self,
        description: str,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        assumption = Assumption(
            description=description,
            requires_validation=True,
        )

        current = list(
            runtime.state.get("assumptions", [])
        )

        if not any(
                item.description == description
                for item in current
        ):
            current.append(assumption)

        return Command(
            update={
                "assumptions": current,
            }
        )

    async def _arun(
        self,
        description: str,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(
            description,
            runtime
        )


class AddMissingInformationTool(
    StateMutationTool
):
    name: str = "add_missing_information"
    description: str = (
        "Registra información faltante que debe ser validada "
        "con el cliente. No asumir valores no proporcionados."
    )

    args_schema: type[BaseModel] = AddMissingInformationInput

    def _run(
        self,
        description: str,
        criticality: Criticality,
        reason: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        item = MissingInformation(
            description=description,
            criticality=criticality,
            reason=reason,
        )

        current = list(
            runtime.state.get(
                "missing_information",
                [],
            )
        )

        if not any(
                x.description == description
                for x in current
        ):
            current.append(item)

        return Command(
            update={
                "missing_information": current,
                "status": "awaiting_client_information",
            }
        )

    async def _arun(
        self,
        description: str,
        criticality: Criticality,
        reason: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(description, criticality, reason, runtime)


class AddClientQuestionTool(
    StateMutationTool
):
    name: str = "add_client_question"
    description: str = (
        "Registra una pregunta concreta para el cliente. "
        "Utilizar únicamente para resolver ambigüedades, "
        "confirmar alcance o completar información necesaria."
    )

    args_schema: type[BaseModel] = AddClientQuestionInput

    def _run(
        self,
        question: str,
        reason: str,
        related_to: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        item = ClientQuestion(
            question=question,
            reason=reason,
            related_to=related_to,
        )

        current = list(
            runtime.state.get(
                "client_questions",
                [],
            )
        )

        if not any(
                x.question == question
                for x in current
        ):
            current.append(item)

        return Command(
            update={
                "client_questions": current,
                "status": "awaiting_client_information",
            }
        )

    async def _arun(
        self,
        question: str,
        reason: str,
        related_to: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(question, reason, related_to, runtime)


class AddActorTool(
    StateMutationTool
):
    name: str = "add_actor"
    description: str = (
        "Registra un actor identificado durante el análisis funcional. "
        "Solo utilizar información explícitamente proporcionada."
    )

    args_schema: type[BaseModel] = AddActorInput

    def _run(
        self,
        name: str,
        actor_type: str,
        responsibility: str,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ):
        runtime = self._validate_runtime(runtime)

        actor = Actor(
            name=name,
            type=actor_type,
            responsibility=responsibility,
        )

        current = list(
            runtime.state.get("actors", [])
        )

        if not any(
                x.name == name
                for x in current
        ):
            current.append(actor)

        return Command(
            update={
                "actors": current,
            }
        )

    async def _arun(
        self,
        name: str,
        actor_type: str,
        responsibility: str,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(name, actor_type, responsibility, runtime)


class AddProcessTool(
    StateMutationTool
):
    name: str = "add_process"
    description: str = (
        "Registra un proceso funcional identificado durante el análisis. "
        "No introducir pasos técnicos ni decisiones de arquitectura."
    )

    args_schema: type[BaseModel] = AddProcessInput

    def _run(
        self,
        name: str,
        objective: str,
        actors: list[str],
        main_flow: list[str],
        exceptions: list[str],
        result: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ):
        runtime = self._validate_runtime(runtime)

        process = Process(
            name=name,
            objective=objective,
            actors=actors,
            main_flow=main_flow,
            exceptions=exceptions,
            result=result,
        )

        current = list(
            runtime.state.get("processes", [])
        )

        current = [
            item
            for item in current
            if item.name != name
        ]

        current.append(process)

        return Command(
            update={
                "processes": current,
            }
        )

    async def _arun(
        self,
        name: str,
        objective: str,
        actors: list[str],
        main_flow: list[str],
        exceptions: list[str],
        result: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(name, objective, actors, main_flow, exceptions, result, runtime)


class UpdateScopeTool(
    StateMutationTool
):
    name: str = "update_scope"
    description: str = (
        "Actualiza el alcance funcional separando elementos "
        "incluidos, excluidos y pendientes de confirmación."
    )

    args_schema: type[BaseModel] = UpdateScopeInput

    def _run(
        self,
        included: list[str],
        excluded: list[str],
        to_confirm: list[str],
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        return Command(
            update={
                "scope": ProposalScope(
                    included=included,
                    excluded=excluded,
                    to_confirm=to_confirm,
                )
            }
        )

    async def _arun(
        self,
        included: list[str],
        excluded: list[str],
        to_confirm: list[str],
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(included, excluded, to_confirm, runtime)


class AddIntegrationTool(
    StateMutationTool
):
    name: str = "add_integration"
    description: str = (
        "Registra una integración funcional identificada. "
        "No seleccionar protocolos, tecnologías o servicios técnicos."
    )

    args_schema: type[BaseModel] = AddIntegrationInput

    def _run(
        self,
        system: str,
        purpose: str,
        data: list[str],
        direction: str | None = None,
        frequency: str | None = None,
        status: str = "To Be Defined",
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        integration = Integration(
            system=system,
            purpose=purpose,
            data=data,
            direction=direction,
            frequency=frequency,
            status=status,
        )

        current = list(
            runtime.state.get("integrations", [])
        )

        current.append(integration)

        return Command(
            update={
                "integrations": current,
            }
        )

    async def _arun(
        self,
        system: str,
        purpose: str,
        data: list[str],
        direction: str | None = None,
        frequency: str | None = None,
        status: str = "To Be Defined",
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(system, purpose, data, direction, frequency, status, runtime)


class AddFunctionalRiskTool(
    StateMutationTool
):
    name: str = "add_functional_risk"
    description: str = (
        "Registra un riesgo funcional relacionado con "
        "ambigüedades, dependencias, restricciones o vacíos."
    )

    args_schema: type[BaseModel] = AddFunctionalRiskInput

    def _run(
        self,
        description: str,
        impact: str,
        cause: str,
        action_or_validation: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        runtime = self._validate_runtime(runtime)

        risk = Risk(
            description=description,
            impact=impact,
            cause=cause,
            action_validation=action_or_validation,
        )

        current = list(
            runtime.state.get("risks", [])
        )

        current.append(risk)

        return Command(
            update={
                "risks": current,
            }
        )

    async def _arun(
        self,
        description: str,
        impact: str,
        cause: str,
        action_or_validation: str | None = None,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> Command:
        return self._run(description, impact, cause, action_or_validation, runtime)


class GetAnalysisStatusTool(
    BaseTool
):
    name: str = "get_analysis_status"
    description: str = (
        "Obtiene el estado actual del análisis funcional, "
        "incluyendo requisitos, información faltante y preguntas abiertas."
    )

    args_schema: type[BaseModel] = GetAnalysisStatusInput

    def _run(
        self,
        include_details: bool = False,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> str:
        if runtime is None:
            raise ToolException(
                "Runtime is required."
            )

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
            "status": state.get("status"),
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

    async def _arun(
        self,
        include_details: bool = False,
        runtime: ToolRuntime[TechDocReqScoutState] | None = None,
    ) -> str:
        return self._run(include_details, runtime)