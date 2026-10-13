import json
import re

from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from settings import BaseModelSettings
from src.prompts import PRESENTATION_SYSTEM_PROMPT
from src.services.document_service import DocumentInput, DocumentService
from src.shared import NarrativeDraft
from src.state.presentation import PresentationAgentState

tools = []

_COMMON_CODES = "USD|SOL"

def _money_pattern(currency: str) -> re.Pattern[str]:
    codes = _COMMON_CODES + ("|" + re.escape(currency) if currency else "")
    return re.compile(rf"(?:[$€£¥]|\b(?:{codes})\b)\s?\d[\d,.]*")

class PresentationAgent:
    """
    """
    def __init__(self, document_service: DocumentService):
        self._name = "presentation-agent",
        self._model_settings = BaseModelSettings()
        self._model = init_chat_model(
            model=self._model_settings.model_name,
            model_provider=self._model_settings.provider,
            temperature=self._model_settings.temperature,
        )
        self._system_prompt = PRESENTATION_SYSTEM_PROMPT
        self._document_service = document_service
        self._agent = create_agent(
            model=self._model,
            tools=tools,
            system_prompt=self._system_prompt,
            middleware=[
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
            ],
            name=self._name,
            response_format=NarrativeDraft
        )

    @staticmethod
    def _prompt(s: PresentationAgentState) -> str:
        data = {
            "customer": s.customer_name or s.requirements.customer_name,
            "title_hint": s.title,
            "context": s.requirements.context,
            "business_problem": s.requirements.problem_need,
            "objectives": s.requirements.objectives,
            "expected_outcomes": s.requirements.expected_results,
            "solution_overview": s.technical.solution_overview,
            "executive_summary_from_architect": s.technical.executive_summary,
            "phases": [{"name": p.name, "objective": p.objective, "weeks": p.duration_weeks} for p in
                       s.technical.implementation_phases],
            "estimated_duration": s.estimate.estimated_duration,
        }
        return "Escribe las secciones narrativas.\n\n" + json.dumps(data, indent=1, default=str)

    @staticmethod
    def _sanitise(n: NarrativeDraft, title: str, currency: str = "") -> NarrativeDraft:
        """Strip any monetary figure from prose: money is shown only from the approved tables."""
        pattern = _money_pattern(currency)

        def clean(text: str) -> str:
            return pattern.sub("[Ver la sección financiera]", text or "")

        return NarrativeDraft(
            proposal_title=(n.proposal_title or title).strip()[:120],
            executive_summary=clean(n.executive_summary),
            context_introduction=clean(n.context_introduction),
            solution_introduction=clean(n.solution_introduction),
            delivery_introduction=clean(n.delivery_introduction),
            financial_introduction=clean(n.financial_introduction),
            closing_statement=clean(n.closing_statement),
        )

    async def arun(self, state: PresentationAgentState, config, document_version: int) -> PresentationAgentState:
        state = state.model_copy(deep=True)
        prompt = self._prompt(state)
        draft: NarrativeDraft = await self._agent.ainvoke({
            "messages": [
                HumanMessage(content=prompt)
            ]
        })
        # draft["structured_response"]
        state.narrative = self._sanitise(draft, state.title, state.estimate.currency)

        state.document = self._document_service.generate(
            DocumentInput(
                proposal_id=state.proposal_id,
                document_version=document_version,
                title=state.title,
                customer_name=state.customer_name,
                requirements=state.requirements,
                technical=state.technical,
                estimate=state.estimate,
                approval=state.approval,
                narrative=state.narrative,
            )
        )
        return state

    def unwrap(self):
        return self._agent

