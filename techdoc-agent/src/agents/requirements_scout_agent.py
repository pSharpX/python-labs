import json
from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import ValidationError

from config import serde
from src.core.exceptions import LLMError
from settings import BaseModelSettings
from src.shared.enums import RequirementStatus
from src.shared.models import RequirementsSpecification, Requirements
from src.prompts import REQUIREMENTS_SYSTEM_PROMPT
from src.state.requirements import RequirementsAgentState
from src.utils.logging import get_logger


log = get_logger(__name__)

tools = []

class RequirementsScoutAgent:
    """
    Agente especializado en el levantamiento y análisis de requerimientos.

    Identifica y estructura las necesidades del cliente, transforma los
    requerimientos en objetivos de negocio claros y establece criterios
    de aceptación verificables.

    Su propósito es construir un brief funcional completo que sirva como
    base para las siguientes etapas del proceso de preventa.
    """
    def __init__(self):
        self._name="requirements-agent"
        self._max_turns: int = 30
        self._model_settings = BaseModelSettings()
        self._model = init_chat_model(
            model=self._model_settings.model_name,
            model_provider=self._model_settings.provider,
            temperature=self._model_settings.temperature,
        )
        self._system_prompt = REQUIREMENTS_SYSTEM_PROMPT
        self._agent = create_agent(
            model=self._model,
            tools=tools,
            system_prompt=self._system_prompt,
            middleware=[
                #CustomGuardsMiddleware(),
                #PIIMiddleware("api_key", detector=r"sk-[a-zA-Z0-9]{32}", strategy="block"),
                #PIIMiddleware("credit_card", strategy="mask"),
                #PIIMiddleware("email", strategy="redact"),
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
            ],
            name=self._name,
            response_format=Requirements,
            checkpointer=InMemorySaver(serde=serde)
        )

    def _prompt(self, state: RequirementsAgentState) -> str:
        previous = (
            state.spec.model_dump_json(
                exclude={"proposal_id", "version", "status", "waiting_for_customer", "validation_issues"}, indent=1
            )
            if state.spec
            else "ninguno (primera interacción)"
        )
        history = "\n".join(f"{t.role.upper()}: {t.content}" for t in state.conversation[-self._max_turns:])
        return (
            "Actualiza la especificación de requerimientos.\n\n"
            f"Especificación anterior (JSON):\n{previous}\n\n"
            f"Conversación hasta ahora:\n{history or '(empty)'}\n\n"
            f"Último mensaje del usuario:\n{state.latest_user_message or '(none)'}\n\n"
            "Devuelve la especificación actualizada completa."
        )

    def run(self, state: RequirementsAgentState, config, version: int) -> RequirementsSpecification:
        last_error: Exception | None = None
        messages = [HumanMessage(content=self._prompt(state))]
        for attempt in range(2):
            try:
                result = self._agent.invoke({
                    "messages": messages,
                })
                content: Requirements = Requirements.model_validate(result["structured_response"])

                return RequirementsSpecification(
                    **content.model_dump(),
                    proposal_id=state.proposal_id,
                    version=version,
                    status=RequirementStatus.IN_PROGRESS,
                )
            except ValidationError as exc:
                last_error = exc
                log.warning("Structured output invalid for %s (attempt %d)", self._name, attempt + 1)
                messages = messages + [
                    HumanMessage(
                        content=f"Tu respuesta anterior no coincide con el esquema: {exc.errors()[:5]}. Devuelve un objeto válido.")
                ]
            except Exception as exc:  # provider errors
                raise LLMError(f"LLM call failed for {self._name}: {type(exc).__name__}") from exc
        raise LLMError(f"LLM returned invalid structured output for {self._name}") from last_error



    async def arun(self, state: RequirementsAgentState, config, version: int) -> RequirementsSpecification:
        last_error: Exception | None = None
        messages = [HumanMessage(content=self._prompt(state))]
        for attempt in range(2):
            try:
                result = await self._agent.ainvoke({
                    "messages": messages,
                })
                content: Requirements = Requirements.model_validate(result["structured_response"])

                return RequirementsSpecification(
                    **content.model_dump(),
                    proposal_id=state.proposal_id,
                    version=version,
                    status=RequirementStatus.IN_PROGRESS,
                )
            except ValidationError as exc:
                last_error = exc
                log.warning("Structured output invalid for %s (attempt %d)", self._name, attempt + 1)
                messages = messages + [
                    HumanMessage(
                        content=f"Tu respuesta anterior no coincide con el esquema: {exc.errors()[:5]}. Devuelve un objeto válido.")
                ]
            except Exception as exc:  # provider errors
                raise LLMError(f"LLM call failed for {self._name}: {type(exc).__name__}") from exc
        raise LLMError(f"LLM returned invalid structured output for {self._name}") from last_error

    def unwrap(self):
        return self._agent


class RequirementsValidator:
    """Configurable readiness rules per service category (``config/validation_rules.json``)."""

    def __init__(self, rules: dict[str, Any]) -> None:
        self._rules = rules

    @classmethod
    def from_file(cls, path: Path) -> "RequirementsValidator":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def _rules_for(self, category: str) -> dict[str, Any]:
        base = dict(self._rules.get("default", {}))
        cat = self._rules.get("categories", {}).get(category, {})
        merged = {
            "required_text": list(dict.fromkeys(base.get("required_text", []) + cat.get("required_text", []))),
            "min_items": {**base.get("min_items", {}), **cat.get("min_items", {})},
            "block_on_blocking_missing_information": cat.get(
                "block_on_blocking_missing_information", base.get("block_on_blocking_missing_information", True)
            ),
        }
        return merged

    @staticmethod
    def _get(obj: Any, path: str) -> Any:
        for part in path.split("."):
            obj = getattr(obj, part, None) if not isinstance(obj, dict) else obj.get(part)
            if obj is None:
                return None
        return obj

    def validate(self, spec: RequirementsSpecification) -> list[str]:
        rules = self._rules_for(spec.service_category)
        issues: list[str] = []
        for path in rules["required_text"]:
            value = self._get(spec, path)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"Missing required information: {path.replace('_', ' ')}")
        for path, minimum in rules["min_items"].items():
            value = self._get(spec, path) or []
            if len(value) < int(minimum):
                issues.append(f"At least {minimum} item(s) required for {path.replace('_', ' ')} (have {len(value)})")
        if rules["block_on_blocking_missing_information"]:
            for gap in spec.missing_information:
                if gap.blocking:
                    issues.append(f"Blocking gap: {gap.topic} — {gap.reason}")
        return issues

    def apply(self, spec: RequirementsSpecification) -> RequirementsSpecification:
        """Set the final status. ``ready`` requires the analyst's judgment AND passing rules."""
        issues = self.validate(spec)
        spec = spec.model_copy(deep=True)
        spec.validation_issues = issues
        if not issues and spec.ready_for_architecture:
            spec.status = RequirementStatus.READY
            spec.waiting_for_customer = False
        else:
            # INVALID: nothing usable captured yet (e.g. off-topic input); otherwise awaiting answers.
            empty = not (spec.problem_need or spec.functional_requirements or spec.objectives)
            spec.status = RequirementStatus.INVALID if empty else RequirementStatus.AWAITING_USER
            spec.waiting_for_customer = True
            if not spec.client_questions:
                spec.client_questions = [self._question_for(i) for i in issues[:5]] or [
                    "¿Podrías compartir más detalles sobre la necesidad del negocio, los objetivos y el alcance esperado?"
                ]
        return spec

    @staticmethod
    def _question_for(issue: str) -> str:
        return f"¿Podría aclarar lo siguiente?? {issue}"
