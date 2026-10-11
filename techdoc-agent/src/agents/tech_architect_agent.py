from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import ValidationError

from config import serde
from src.core.exceptions import LLMError
from settings import BaseModelSettings
from src.shared.enums import TechnicalStatus
from src.shared.models import TechnicalDesignContent, TechnicalProposal
from src.prompts import ARCHITECT_SYSTEM_PROMPT
from src.tools.mcp import MCPSettings, MCPToolsAdapter
from src.state.architect import TechArchitectAgentState
from src.utils.logging import get_logger


log = get_logger(__name__)

tools = []

class TechArchitectAgent:
    """
    Agente especializado en arquitectura y diseño de soluciones tecnológicas.

    Analiza los requerimientos funcionales y no funcionales del cliente,
    identifica restricciones, dependencias, integraciones y necesidades
    técnicas, y propone una arquitectura de solución coherente con el
    contexto del negocio.

    Utiliza las herramientas técnicas disponibles, incluyendo herramientas
    proporcionadas por servidores MCP, para consultar documentación y
    capacidades actualizadas de las plataformas y servicios tecnológicos.

    Evalúa alternativas arquitectónicas, identifica trade-offs y documenta
    las decisiones técnicas, supuestos, riesgos y dependencias relevantes.

    Su propósito es transformar el brief de requerimientos en una propuesta
    técnica y arquitectónica que sirva como base para las siguientes etapas
    del proceso de preventa.
    """
    def __init__(self, mcp_adapter: MCPToolsAdapter):
        self._name = "techdoc-architect-agent"
        self._model_settings = BaseModelSettings()
        self._model = init_chat_model(
            model=self._model_settings.model_name,
            model_provider=self._model_settings.provider,
            temperature=self._model_settings.temperature,
        )
        self._system_prompt = ARCHITECT_SYSTEM_PROMPT

        self._mcp_settings = MCPSettings()
        self._mcp_adapter = mcp_adapter
        mcp_tools = self._mcp_adapter.get_tools(
            allowed_tools=self._mcp_settings.allowed_tools
        )
        tools.extend(mcp_tools)
        self._agent = create_agent(
            model=self._model,
            tools=tools,
            system_prompt=self._system_prompt,
            name=self._name,
            response_format=TechnicalDesignContent,
            checkpointer=InMemorySaver(serde=serde)
        )

    @staticmethod
    def _design_prompt(state: TechArchitectAgentState, issues: list[str] | None) -> str:
        parts = [
            "Especificación de requerimientos (validada):",
            state.requirements.model_dump_json(
                exclude={"client_questions", "validation_issues", "change_summary"}, indent=1)
            ,
        ]
        if state.feedback:
            parts.append(f"\nComentarios del usuario por atender:\n{state.feedback}")
        if issues:
            parts.append("\nTu diseño anterior tenía estos problemas; corrígelos:\n- " + "\n- ".join(issues))
        return "\n".join(parts)

    @staticmethod
    def _structural_issues(design: TechnicalDesignContent) -> list[str]:
        issues: list[str] = []
        if not design.phase_activities:
            issues.append("No implementation phases defined")
        if not design.phase_activities:
            issues.append("No phase activities defined")
        if not design.deliverables:
            issues.append("No deliverables defined")
        if design.timeline_estimation.total_duration_weeks <= 0:
            issues.append("Total duration must be positive")
        return issues

    def run(self, state: TechArchitectAgentState, config, version: int) -> TechArchitectAgentState:
        state = state.model_copy(deep=True)
        req = state.requirements
        base = dict(proposal_id=state.proposal_id, version=version,
                    based_on_requirements_fingerprint=state.requirements_fingerprint,
                    based_on_requirements_version=req.version)
        last_error: Exception | None = None
        issues: list[str] | None = None
        messages = [HumanMessage(content=self._design_prompt(state, issues))]
        for attempt in range(2):
            try:
                design: TechnicalDesignContent = self._agent.invoke({
                    "messages": messages,
                })
                issues = self._structural_issues(design)
                if not issues:
                    break
                if issues:
                    status = TechnicalStatus.FAILED
                elif any(q.blocking for q in design.open_questions):
                    status = TechnicalStatus.NEEDS_CLARIFICATION
                else:
                    status = TechnicalStatus.READY
                state.output = TechnicalProposal(
                    **base, status=status,
                    executive_summary=design.executive_summary, solution_overview=design.solution_overview,
                    architecture=design.architecture, architecture_components=design.architecture_components,
                    technology_decisions=design.technology_decisions, integrations=design.integrations,
                    implementation_phases=sorted(design.implementation_phases, key=lambda p: p.order),
                    phase_activities=design.phase_activities, deliverables=design.deliverables,
                    acceptance_criteria=design.acceptance_criteria, required_profiles=design.required_profiles,
                    timeline_estimation=design.timeline_estimation, prerequisites=design.prerequisites,
                    technical_risks=design.technical_risks,
                    scope=design.scope, out_of_scope=design.out_of_scope, assumptions=design.assumptions,
                    constraints=design.constraints, documentation_sources=design.documentation_sources,
                    open_questions=design.open_questions,
                    validation_issues=issues,
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

    async def arun(self, state: TechArchitectAgentState, config, version: int) -> TechArchitectAgentState:
        state = state.model_copy(deep=True)
        req = state.requirements
        base = dict(proposal_id=state.proposal_id, version=version,
                    based_on_requirements_fingerprint=state.requirements_fingerprint,
                    based_on_requirements_version=req.version)
        last_error: Exception | None = None
        issues: list[str] | None = None
        messages = [HumanMessage(content=self._design_prompt(state, issues))]
        for attempt in range(2):
            try:
                design: TechnicalDesignContent = await self._agent.ainvoke({
                    "messages": messages,
                })
                issues = self._structural_issues(design)
                if not issues:
                    break
                if issues:
                    status = TechnicalStatus.FAILED
                elif any(q.blocking for q in design.open_questions):
                    status = TechnicalStatus.NEEDS_CLARIFICATION
                else:
                    status = TechnicalStatus.READY
                state.output = TechnicalProposal(
                    **base, status=status,
                    executive_summary=design.executive_summary, solution_overview=design.solution_overview,
                    architecture=design.architecture, architecture_components=design.architecture_components,
                    technology_decisions=design.technology_decisions, integrations=design.integrations,
                    implementation_phases=sorted(design.implementation_phases, key=lambda p: p.order),
                    phase_activities=design.phase_activities, deliverables=design.deliverables,
                    acceptance_criteria=design.acceptance_criteria, required_profiles=design.required_profiles,
                    timeline_estimation=design.timeline_estimation, prerequisites=design.prerequisites,
                    technical_risks=design.technical_risks,
                    scope=design.scope, out_of_scope=design.out_of_scope, assumptions=design.assumptions,
                    constraints=design.constraints, documentation_sources=design.documentation_sources,
                    open_questions=design.open_questions,
                    validation_issues=issues,
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
        return self._agent

