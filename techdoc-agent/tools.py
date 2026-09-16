
from abc import ABC
from pathlib import Path
from typing import Generic, TypeVar, Type

from langchain_core.tools import BaseTool, ToolException
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from pydantic import BaseModel

from state import TechDocReqScoutState, Priority, Requirement
from tools_input import SaveMarkdownInput, UpdateFunctionalRequirementInput


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

class StateMutationTool(
    BaseTool,
    Generic[StateT],
    ABC,
):
    """
    Base class for tools that mutate LangGraph agent state.
    """

    def _validate_runtime(
        self,
        runtime: ToolRuntime[StateT] | None,
    ) -> ToolRuntime[StateT]:
        if runtime is None:
            raise ToolException(
                "Runtime is required for state mutation."
            )

        return runtime


class UpdateFunctionalRequirementTool(
    StateMutationTool[TechDocReqScoutState]
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