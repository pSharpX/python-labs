from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from config import serde
from settings import BaseModelSettings
from src.routing import route_after_requirements, route_after_technical, route_after_financial, route_after_approval
from src.shared import ProposalRevision, ProposalStatus
from src.state.financial_estimator import FinancialEstimatorOutputSchema, FinancialEstimatorAgentState
from src.state.requirements import RequirementsOutputSchema, RequirementsAgentState
from src.agents import TechArchitectAgent, RequirementsScoutAgent, FinancialEstimatorAgent
from .configs import langfuse_handler
from src.state import WorkflowState
from .state.architect import TechArchitectOutputSchema, TechArchitectAgentState
from src.tools.mcp import MCPToolsAdapter, MCPSettings
from src.tools.requirements import SaveMarkdownTool


class TechDocBuilderGraph:
    """A langgraph powered workflow that design and write technical-functional proposals and financial documents."""

    def __init__(self):
        self.__settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__settings.model_name,
            model_provider=self.__settings.provider,
            temperature=self.__settings.temperature,
        )
        self.__builder = StateGraph(
            state_schema=WorkflowState,
        )
        self.__tool = SaveMarkdownTool()
        self.__mcp_settings = MCPSettings()
        self.__mcp_adapter = MCPToolsAdapter.create(self.__mcp_settings)

        # Initialize agents
        self.__req_scout_agent = RequirementsScoutAgent()
        self.__tech_architect_agent = TechArchitectAgent(
            mcp_adapter=self.__mcp_adapter
        )
        self.__financial_estimator_agent = FinancialEstimatorAgent()

        # Initialize workflow
        self.graph = self.__build()

    @staticmethod
    def initialize_proposal(state: WorkflowState):
        revision_request = state.get("revision_request")
        if state.get("proposal_id") and revision_request:
            revision = state.get("revision", 0) + 1
            previous = state.get("requirements") or {}
            req_version = previous.get("version", revision - 1)
            changed_fields = ["raw_requirements"]
            new_req = dict(previous)
            new_req["raw_requirements"] = revision_request
            new_req["version"] = req_version + 1
            new_req["ready_for_architecture"] = False
            new_req["status"] = ProposalStatus.ANALYZING_REQUIREMENTS.value
            tech = state.get("technical_architecture")
            fin = state.get("financial_estimation")
            if tech:
                tech = dict(tech)
                tech["stale"] = True
                tech["status"] = "stale"
            if fin:
                fin = dict(fin)
                fin["stale"] = True
                fin["approval_status"] = "invalidated"
                fin["status"] = "stale"
            return {
                "user_request": revision_request,
                "revision_request": None,
                "revision": revision,
                "requirements": new_req,
                "technical_architecture": tech,
                "financial_estimation": fin,
                "status": ProposalStatus.ANALYZING_REQUIREMENTS.value,
                "current_stage": "requirements",
                "revisions": state.get("revision_history", []) + [ProposalRevision(
                    revision=revision,
                    changed_by="user",
                    changed_fields=changed_fields,
                    reason=state.get("revision_reason"),
                )],
            }
        return {
            "proposal_id": state.get("proposal_id", "proposal-unknown"),
            "revision": state.get("revision", 1),
            "status": ProposalStatus.ANALYZING_REQUIREMENTS.value,
            "current_stage": "requirements",
            "errors": state.get("errors", []),
            "revisions": state.get("revision_history", []),
        }

    def __requirements_agent_node(self, state: WorkflowState):
        """Requirements-scout Node capture business requirements, objectives and define acceptance criteria."""

        req_state = state.get("requirements") or {}
        raw = req_state.get("raw_requirements") or state.get("user_request", "")
        version = req_state.get("version", state.get("revision", 1))

        res: RequirementsOutputSchema = self.__req_scout_agent.run(raw)

        return {
            "requirements": {
                **res.model_dump(),
                "raw_requirements": raw,
                "version": version,
                "status": (
                    ProposalStatus.REQUIREMENTS_READY.value if res.ready_for_architecture else ProposalStatus.AWAITING_REQUIREMENTS.value
                )
            },
            "status": ProposalStatus.REQUIREMENTS_READY.value if res.ready_for_architecture else ProposalStatus.AWAITING_REQUIREMENTS.value
        }

    @staticmethod
    def awaiting_requirements(state: WorkflowState):
        req: RequirementsAgentState = state["requirements"]
        response = interrupt({
            "type": "requirements_clarification",
            "message": "Los requisitos aún están incompletos. Por favor, comparte la información que falta para que podamos continuar.",
            "questions": req.get("client_questions", []),
            "missing_information": [
                x if isinstance(x, dict) else x.model_dump() for x in
                                    req.get("missing_information", [])
            ],
        })

        if not isinstance(response, dict) or not response.get("raw_requirements"):
            raise ValueError("Resume payload must contain raw_requirements")
        merged = dict(req)
        merged["raw_requirements"] = response["raw_requirements"]

        return {
            "requirements": merged,
            "user_request": response["raw_requirements"],
            "status": ProposalStatus.ANALYZING_REQUIREMENTS.value
        }

    def __tech_architect_agent_node(self, state: WorkflowState):
        """Technical Architect Node design and implement the technical solution based on functional requirements."""

        reqs = state["requirements"]
        current_ver = state["technical_architecture"]["version"] + 1 if state.get("technical_architecture") else 1

        if not reqs or not reqs.get("ready_for_architecture"):
            return {
                "status": ProposalStatus.ERROR.value,
                "errors": state.get("errors", []) + ["Datos incompletos para continuarr"]
            }

        res: TechArchitectOutputSchema = self.__tech_architect_agent.run(reqs)

        tech_state: TechArchitectAgentState = {
            **res.model_dump(),
            "requirements_version": reqs["version"],
            "status": ProposalStatus.TECHNICAL_PROPOSAL_READY.value,
            "stale": False,
            "version": current_ver,
        }

        return {
            "technical_architecture": tech_state,
            "status": ProposalStatus.TECHNICAL_PROPOSAL_READY.value,
            "current_stage": "technical_architecture"
        }

    def __financial_estimator_agent_node(self, state: WorkflowState):
        """Financial Estimator Node calculate the effort, the cost and commercial conditions."""

        reqs = state["requirements"]
        tech = state["technical_architecture"]
        current_ver = state["financial_estimation"]["version"] + 1 if state.get("financial_estimation") else 1

        if not reqs or not tech or tech.get("stale") or tech.get("requirements_version") != reqs.get("version"):
            raise ValueError("No se puede estimar a partir de una propuesta técnica desactualizada.")

        res: FinancialEstimatorOutputSchema = self.__financial_estimator_agent.run(
            requirements=reqs,
            technical_proposal=tech,
            catalog=[],
         )

        fin_state: FinancialEstimatorAgentState = {
            "technical_proposal_version": tech["version"],
            #"service_items": service_items,
            "effort_breakdown": res.effort_breakdown,
            #"hourly_rate": subtotal / total_hours if total_hours > 0 else Decimal("0.00"),
            #"estimated_hours": total_hours,
            "currency": "USD",
            "assumptions": res.assumptions,
            "financial_proposal": res.financial_proposal,
            "approval_status": "pending",
            "user_feedback": None,
            "status": ProposalStatus.AWAITING_FINANCIAL_APPROVAL.value,
            "version": current_ver,
            "stale": False,
        }

        financial = {
            **res.model_dump(),
            #"service_items": [x.model_dump() for x in services],
            #"estimated_hours": sum((x.hours for x in services), Decimal("0")),
            #"subtotal": subtotal,
            #"taxes": taxes,
            #"total": total,
            "technical_proposal_version": tech["version"],
            "version": current_ver,
            "approval_status": "pending",
            "status": ProposalStatus.AWAITING_FINANCIAL_APPROVAL.value,
            "stale": False
        }

        return {
            "financial_estimation": financial,
            "status": ProposalStatus.AWAITING_FINANCIAL_APPROVAL.value,
            "current_stage": "financial_proposal_built"
        }

    @staticmethod
    def request_financial_approval(state: WorkflowState):
        financial = state["financial_estimation"]
        response = interrupt({
            "type": "financial_approval",
            "proposal": financial,
            "message": "Revise la propuesta financiera y apruébela o solicite cambios.",
            "allowed_actions": ["approve", "request_changes"],
        })
        if not isinstance(response, dict):
            raise ValueError("Approval response must be an object")
        action = response.get("action")
        if action == "approve":
            updated = dict(financial)
            updated["approval_status"] = "approved"
            updated["status"] = ProposalStatus.APPROVED.value
            return {
                "financial_estimation": updated,
                "status": ProposalStatus.APPROVED.value
            }
        if action == "request_changes":
            updated = dict(financial)
            updated["approval_status"] = "changes_requested"
            updated["user_feedback"] = response.get("feedback", "")
            return {
                "financial_estimation": updated,
                "status": ProposalStatus.REVISION_REQUIRED.value
            }
        raise ValueError("action must be approve or request_changes")

    @staticmethod
    def failed_node(state: WorkflowState):
        return {
            "current_stage": "failed",
            "status": ProposalStatus.ERROR.value
        }

    @staticmethod
    def complete_node(state: WorkflowState):
        financial = state.get("financial_estimation") or {}
        if financial.get("approval_status") != "approved":
            raise ValueError("Cannot complete without financial approval")
        return {
            "status": ProposalStatus.COMPLETED.value,
            "current_stage": "completed"
        }

    @staticmethod
    def is_technical_current(state: WorkflowState) -> bool:
        req, tech = state.get("requirements"), state.get("technical_architecture")
        return bool(req and tech and not tech.get("stale") and tech.get("requirements_version") == req.get("version"))

    @staticmethod
    def is_financial_current(state: WorkflowState) -> bool:
        tech, fin = state.get("technical_architecture"), state.get("financial_estimation")
        return bool(TechDocBuilderGraph.is_technical_current(state) and fin and not fin.get("stale") and fin.get(
            "technical_proposal_version") == tech.get("version"))

    def __build(self):
        self.__builder.add_node("initialize_proposal", self.initialize_proposal)
        self.__builder.add_node("requirements_agent", self.__requirements_agent_node)
        self.__builder.add_node("awaiting_requirements", self.awaiting_requirements)
        self.__builder.add_node("technical_architect", self.__tech_architect_agent_node)
        self.__builder.add_node("financial_estimator", self.__financial_estimator_agent_node)
        self.__builder.add_node("request_financial_approval", self.request_financial_approval)
        self.__builder.add_node("complete", self.complete_node)
        self.__builder.add_node("failed", self.failed_node)

        self.__builder.add_edge(START, "initialize_proposal")
        self.__builder.add_edge("initialize_proposal", "requirements_agent")
        self.__builder.add_conditional_edges("requirements_agent", route_after_requirements)
        self.__builder.add_edge("awaiting_requirements", "requirements_agent")
        self.__builder.add_conditional_edges("technical_architect", route_after_technical)
        self.__builder.add_conditional_edges("financial_estimator", route_after_financial)
        self.__builder.add_conditional_edges("request_financial_approval", route_after_approval, {
            "complete": "complete",
            "financial_estimator": "financial_estimator",
        })
        self.__builder.add_edge("complete", END)
        self.__builder.add_edge("failed", END)

        return self.__builder.compile(checkpointer=InMemorySaver(serde=serde))

    def invoke(self, question: str, input_obj: dict, session_id: str) -> WorkflowState:
        return self.graph.invoke(
            input={
                "user_request": question,
                "resources": input_obj.get("resources", []),
                "proposal_id": "proposal-demo-001",
            },
            config={
                "callbacks": [
                    langfuse_handler,
                ],
                "metadata": {
                    "langfuse_user_id": input_obj["user_id"],
                    "langfuse_session_id": session_id,
                    "langfuse_tags": [
                        "environment:dev",
                        "framework:langgraph",
                        "application:techdoc-builder-workflow",
                        "component:builder-workflow"
                    ]
                },
                "configurable": {
                    "thread_id": session_id
                }
            }
        )

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to TechDoc Builder Workflow, your helpful assistant!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.invoke(question, input_obj, session_id)
            print(state)

    def draw_graph(self):
        self.graph.get_graph().draw_mermaid_png(output_file_path="techdoc_workflow.png")