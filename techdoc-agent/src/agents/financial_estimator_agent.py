import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import ValidationError

from config import serde
from src.core.exceptions import LLMError
from src.services.financial_service import FinancialService
from settings import BaseModelSettings
from src.shared.models import EffortMappingDraft
from src.prompts import FINANCIAL_ESTIMATE_SYSTEM_PROMPT
from src.state.financial_estimator import FinancialEstimatorAgentState
from src.utils.logging import get_logger

log = get_logger(__name__)

tools = [
]

class FinancialEstimatorAgent:
    """
    TODO
    """
    def __init__(self, financial_service: FinancialService):
        self._name = "financial-estimator-agent"
        self.__model_settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__model_settings.model_name,
            model_provider=self.__model_settings.provider,
            temperature=self.__model_settings.temperature,
        )
        self.__system_prompt = FINANCIAL_ESTIMATE_SYSTEM_PROMPT

        self._financial_service = financial_service
        self.__agent = create_agent(
            model=self.__model,
            tools=tools,
            system_prompt=self.__system_prompt,
            name=self._name,
            response_format=EffortMappingDraft,
            checkpointer=InMemorySaver(serde=serde)
        )

    @staticmethod
    def _prompt(state: FinancialEstimatorAgentState) -> str:
        tp = state.technical
        payload = {
            "requested_service": tp.requested_service.model_dump() if tp.requested_service else None,
            "phases": [p.model_dump() for p in tp.implementation_phases],
            "activities": [a.model_dump() for a in tp.phase_activities],
            "deliverables": [d.model_dump() for d in tp.deliverables],
            "authorised_profiles": [{"profile_id": p.role_id, "name": p.role_title, "seniority": p.seniority} for p in
                                    tp.required_profiles],
            "duration": tp.timeline_estimation.model_dump() if tp.timeline_estimation else None,
            "assumptions": tp.assumptions,
            "constraints": tp.constraints,
            "risks": [r for r in tp.technical_risks],
            "out_of_scope": tp.out_of_scope,
        }
        text = (
                "Estimar el esfuerzo para esta propuesta técnica.\n\n"
                + json.dumps(payload, indent=1, default=str)
        )
        if state.feedback:
            text += "\n\nComentarios del usuario sobre la estimación anterior:\n" + state.feedback
        return text

    def run(self, state: FinancialEstimatorAgentState, version: int) -> FinancialEstimatorAgentState:
        state = state.model_copy(deep=True)

        prompt = self._prompt(state)
        last_error: Exception | None = None
        messages = [HumanMessage(content=prompt)]
        for attempt in range(2):
            try:
                draft: EffortMappingDraft = self.__agent.invoke({
                    "messages": messages,
                })
                state.scope_change_detected = bool(state.feedback) and draft.scope_change_detected
                state.output = self._financial_service.calculate(
                    proposal_id=state.proposal_id,
                    version=version,
                    draft=draft,
                    technical=state.technical,
                    technical_fingerprint=state.technical_fingerprint,
                    revision_feedback=state.feedback,
                )
                return state
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

    async def arun(self, state: FinancialEstimatorAgentState, version: int) -> FinancialEstimatorAgentState:
        state = state.model_copy(deep=True)

        prompt = self._prompt(state)
        last_error: Exception | None = None
        messages = [HumanMessage(content=prompt)]
        for attempt in range(2):
            try:
                draft: EffortMappingDraft = await self.__agent.ainvoke({
                    "messages": messages,
                })
                state.scope_change_detected = bool(state.feedback) and draft.scope_change_detected
                state.output = self._financial_service.calculate(
                    proposal_id=state.proposal_id,
                    version=version,
                    draft=draft,
                    technical=state.technical,
                    technical_fingerprint=state.technical_fingerprint,
                    revision_feedback=state.feedback,
                )
                return state
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
        return self.__agent

