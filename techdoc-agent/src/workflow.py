import os
from dataclasses import dataclass
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command

from config import serde
from settings import BaseModelSettings, ApplicationSettings
from src.routing import N, route_after_requirements, route_after_technical, route_after_financial, route_after_approval
from src.shared import ProposalRevision, ProposalStatus, UserApprovalAction, UserResponse, UserAction, Stage, PendingInput
from src.state.financial_estimator import FinancialEstimatorOutputSchema, FinancialEstimatorAgentState
from src.state.requirements import RequirementsOutputSchema, RequirementsAgentState
from src.agents import TechArchitectAgent, RequirementsScoutAgent, FinancialEstimatorAgent
from .configs import langfuse_handler
from src.state import WorkflowState
from .state.architect import TechArchitectOutputSchema, TechArchitectAgentState
from src.tools.mcp import MCPToolsAdapter
from src.tools.requirements import SaveMarkdownTool


@dataclass(frozen=True)
class WorkflowSnapshot:
    """What a caller (API, UI, CLI) needs to know after every step."""

    proposal_id: str
    values: dict[str, Any]
    interrupt: dict[str, Any] | None  # payload the human must answer, if paused

    @property
    def status(self) -> ProposalStatus | None:
        return self.values.get("status")

    @property
    def waiting_for_user(self) -> bool:
        return self.interrupt is not None


class TechDocBuilderGraph:
    """A langgraph powered workflow that design and write technical-functional proposals and financial documents."""

    def __init__(self, mcp_adapter: MCPToolsAdapter):
        self._app_settings = ApplicationSettings()
        self._model_settings = BaseModelSettings()
        self._model = init_chat_model(
            model=self._model_settings.model_name,
            model_provider=self._model_settings.provider,
            temperature=self._model_settings.temperature,
        )
        self._callbacks = [
            langfuse_handler
        ]
        self._builder = StateGraph(
            state_schema=WorkflowState,
        )
        self._tool = SaveMarkdownTool()
        self._mcp_adapter = mcp_adapter

        # Initialize agents
        self._req_scout_agent = RequirementsScoutAgent()
        self._tech_architect_agent = TechArchitectAgent(
            mcp_adapter=self._mcp_adapter
        )
        self._financial_estimator_agent = FinancialEstimatorAgent()

        # Initialize workflow
        self._graph = self._build()

    @staticmethod
    async def _initialize_proposal(state: WorkflowState):
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
                "current_stage": Stage.REQUIREMENTS,
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
            "current_stage": Stage.REQUIREMENTS,
            "errors": state.get("errors", []),
            "revisions": state.get("revision_history", []),
        }

    async def _requirements_agent_node(self, state: WorkflowState, config: RunnableConfig):
        """Requirements-scout Node capture business requirements, objectives and define acceptance criteria."""

        req_state = state.get("requirements") or {}
        raw = req_state.get("raw_requirements") or state.get("user_request", "")
        version = req_state.get("version", state.get("revision", 1))

        res: RequirementsOutputSchema = await self._req_scout_agent.arun(raw, config["configurable"])

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
    async def _awaiting_requirements(state: WorkflowState):
        req: RequirementsAgentState = state["requirements"]
        raw_response = interrupt({
            "type": "requirements_clarification",
            "proposal_id": state.get("proposal_id"),
            "message": "Los requisitos aún están incompletos. Por favor, comparte la información que falta para que podamos continuar.",
            "questions": req.get("client_questions", [ req.get("readiness_reason", "") ]),
            "missing_information": [
                x if isinstance(x, dict) else x.model_dump() for x in
                                    req.get("missing_information", [])
            ],
            #"allowed_actions": [UserAction.PROVIDE_INFORMATION, UserAction.CHANGE_REQUIREMENTS],
        })

        response: UserResponse = UserResponse.model_validate(raw_response)
        if not response.information:
            raise ValueError("Resume payload must contain information")
        merged = dict(req)
        merged["raw_requirements"] = response.information

        return {
            "requirements": merged,
            "user_request": response.information,
            "status": ProposalStatus.ANALYZING_REQUIREMENTS.value
        }

    async def _tech_architect_agent_node(self, state: WorkflowState):
        """Technical Architect Node design and implement the technical solution based on functional requirements."""

        reqs = state["requirements"]
        current_ver = state["technical_architecture"]["version"] + 1 if state.get("technical_architecture") else 1

        if not reqs or not reqs.get("ready_for_architecture"):
            return {
                "status": ProposalStatus.ERROR.value,
                "errors": state.get("errors", []) + ["Datos incompletos para continuarr"]
            }

        res: TechArchitectOutputSchema = await self._tech_architect_agent.arun(reqs)

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

    async def _financial_estimator_agent_node(self, state: WorkflowState):
        """Financial Estimator Node calculate the effort, the cost and commercial conditions."""

        reqs = state["requirements"]
        tech = state["technical_architecture"]
        current_ver = state["financial_estimation"]["version"] + 1 if state.get("financial_estimation") else 1

        if not reqs or not tech or tech.get("stale") or tech.get("requirements_version") != reqs.get("version"):
            raise ValueError("No se puede estimar a partir de una propuesta técnica desactualizada.")

        res: FinancialEstimatorOutputSchema = await self._financial_estimator_agent.arun(
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
    async def _request_financial_approval(state: WorkflowState):
        """Human-in-the-loop: pause for approval of the CURRENT financial estimate."""

        financial = state["financial_estimation"]
        raw_response = interrupt({
            "type": "financial_approval",
            "proposal_id": state.get("proposal_id"),
            "financial_proposal": financial["financial_proposal"],
            "proposal": financial,
            "message": "Revise la propuesta financiera y apruébela o solicite cambios.",
            "allowed_actions": [
                UserAction.APPROVE,
                UserAction.REQUEST_CHANGES,
            ],
        })
        response = UserResponse.model_validate(raw_response)
        action: UserAction = response.action
        if action == UserAction.PROVIDE_INFORMATION:
            raise ValueError("'provide_information' is not valid at financial approval")

        if action == UserAction.APPROVE:
            updated = dict(financial)
            updated["approval_status"] = "approved"
            updated["status"] = ProposalStatus.APPROVED.value
            return {
                "financial_estimation": updated,
                "status": ProposalStatus.APPROVED.value
            }
        if action == UserAction.REQUEST_CHANGES:
            updated = dict(financial)
            updated["approval_status"] = "changes_requested"
            updated["user_feedback"] = response.feedback
            return {
                "financial_estimation": updated,
                "status": ProposalStatus.REVISION_REQUIRED.value
            }
        raise ValueError("action must be approve or request_changes")

    @staticmethod
    async def _failed_node(state: WorkflowState):
        return {
            "current_stage": "failed",
            "status": ProposalStatus.ERROR.value
        }

    @staticmethod
    async def _complete_node(state: WorkflowState):
        financial = state.get("financial_estimation") or {}
        if financial.get("approval_status") != "approved":
            raise ValueError("Cannot complete without financial approval")
        return {
            "status": ProposalStatus.COMPLETED.value,
            "current_stage": "completed"
        }

    @staticmethod
    def _is_technical_current(state: WorkflowState) -> bool:
        req, tech = state.get("requirements"), state.get("technical_architecture")
        return bool(req and tech and not tech.get("stale") and tech.get("requirements_version") == req.get("version"))

    @staticmethod
    def _is_financial_current(state: WorkflowState) -> bool:
        tech, fin = state.get("technical_architecture"), state.get("financial_estimation")
        return bool(TechDocBuilderGraph._is_technical_current(state) and fin and not fin.get("stale") and fin.get(
            "technical_proposal_version") == tech.get("version"))

    def _build(self):
        self._builder.add_node(N.INITIALIZE, self._initialize_proposal)
        self._builder.add_node(N.REQUIREMENTS, self._requirements_agent_node)
        self._builder.add_node(N.AWAITING_REQUIREMENTS, self._awaiting_requirements)
        self._builder.add_node(N.ARCHITECT, self._tech_architect_agent_node)
        self._builder.add_node(N.ESTIMATOR, self._financial_estimator_agent_node)
        self._builder.add_node(N.APPROVAL, self._request_financial_approval)
        self._builder.add_node(N.COMPLETE, self._complete_node)
        self._builder.add_node(N.FAILED, self._failed_node)

        self._builder.add_edge(START, N.INITIALIZE)
        self._builder.add_edge(N.INITIALIZE, N.REQUIREMENTS)
        self._builder.add_conditional_edges(N.REQUIREMENTS, route_after_requirements)
        self._builder.add_edge(N.AWAITING_REQUIREMENTS, N.REQUIREMENTS)
        self._builder.add_conditional_edges(N.ARCHITECT, route_after_technical)
        self._builder.add_conditional_edges(N.ESTIMATOR, route_after_financial)
        self._builder.add_conditional_edges(N.APPROVAL, route_after_approval, {
            "complete": N.COMPLETE,
            "financial_estimator": N.ESTIMATOR,
        })
        self._builder.add_edge(N.COMPLETE, END)
        self._builder.add_edge(N.FAILED, END)

        return self._builder.compile(checkpointer=InMemorySaver(serde=serde))

    def _get_config(self, user_id, session_id) -> dict[str, Any]:
        return {
            "callbacks": self._callbacks,
            "metadata": {
                "langfuse_user_id": user_id,
                "langfuse_session_id": session_id,
                "langfuse_tags": [
                    f"environment:{os.getenv('ENVIRONMENT',"dev")}",
                    "framework:langgraph",
                    f"owner:{self._app_settings.owner}",
                    f"application:{self._app_settings.name}",
                    f"component:{self._app_settings.component}"
                ]
            },
            "configurable": {
                "thread_id": session_id
            }
        }

    async def snapshot(self, thread_id: str) -> WorkflowSnapshot:
        state = await self._graph.aget_state(self._get_config(thread_id, thread_id))
        pending = [i.value for task in state.tasks for i in task.interrupts]
        return WorkflowSnapshot(thread_id, dict(state.values), pending[0] if pending else None)

    def invoke(self, initial_input: dict | Command[Any], session_id: str) -> WorkflowState:
        return self._graph.invoke(
            input=initial_input,
            config=self._get_config(session_id, session_id),
        )

    async def resume(self, thread_id: str, response: UserResponse | dict[str, Any]) -> WorkflowSnapshot:
        """Answer the pending interrupt (requirements questions or financial approval)."""
        payload = response.model_dump(mode="json", exclude_none=True) if isinstance(response,
                                                                                    UserResponse) else response
        await self._graph.ainvoke(Command(resume=payload), self._get_config(thread_id, thread_id))
        return await self.snapshot(thread_id)

    async def start(self, thread_id: str, user_request: str) -> WorkflowSnapshot:
        await self._graph.ainvoke(
            input={
                "proposal_id": thread_id,
                "user_request": user_request,
            },
            config=self._get_config(thread_id, thread_id))
        return await self.snapshot(thread_id)

    async def request_revision(
            self, thread_id: str, changes: str, *, changed_by: str = "user", reason: str | None = None
    ) -> WorkflowSnapshot:
        """Change requirements at any time: mid-flight (paused) or after completion."""
        current = await self.snapshot(thread_id)
        if current.waiting_for_user:
            return await self.resume(
                thread_id,
                UserResponse(
                    action=UserAction.CHANGE_REQUIREMENTS,
                    changes=changes,
                    changed_by=changed_by,
                    reason=reason
                ),
            )
        pending = PendingInput(kind="change", text=changes, changed_by=changed_by, reason=reason)
        await self._graph.ainvoke({"pending_input": pending}, self._get_config(thread_id, thread_id))
        return await self.snapshot(thread_id)

    def legacy_start(self, input_obj: dict, session_id: str):
        print("Welcome to TechDoc Builder Workflow, your helpful assistant!")
        print("Start typing ('c' for exit) >> ")
        config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        proposal_id = f"proposal-{session_id}"
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue

            initial_input = {
                "user_request": question,
                "resources": input_obj.get("resources", []),
                "proposal_id": input_obj.get("proposal_id", proposal_id),
            }
            print(f"=== Starting Proposal Workflow [{proposal_id}] ===")

            state = self.invoke(
                initial_input=initial_input,
                session_id=session_id
            )

            print(f"\n[Stage 1] Current Status: {state['status']}")

            # Check interrupt for missing info if requirements were incomplete
            snapshot = self._graph.get_state(config)
            if snapshot.next and "awaiting_requirements" in snapshot.next:
                print("\n--> Interrupt Triggered: Missing Requirements Information")
                print("Questions:", snapshot.tasks[0].interrupts[0].value["questions"])

                # Resume with clarifications
                self.invoke(
                    initial_input=Command(resume={
                        "raw_requirements": "The system must support 50,000 active daily users using OAuth2 / Microsoft Entra ID."
                    }),
                    session_id=session_id
                )

            # Check next snapshot (Financial Approval Interrupt)
            snapshot = self._graph.get_state(config)
            if snapshot.next and "request_financial_approval" in snapshot.next:
                fin = snapshot.values["financial_estimation"]
                print(f"\n--> Interrupt Triggered: Financial Approval Requested")
                print(f"    Version: Technical v{fin['technical_proposal_version']}")
                print(f"    Total Cost: ${fin['total']} {fin['currency']} ({fin['estimated_hours']} Hours)")

                # Demonstrate Revision Flow: Request Requirement Change (Revisions v2)
                print("\n--- User Requests Requirement Revision (v2) ---")
                self.invoke(
                    initial_input=Command(resume={
                        "action": UserApprovalAction.REVISE_REQUIREMENTS.value,
                        "feedback": "Add multi-region disaster recovery and Azure Cosmos DB storage."
                    }),
                    session_id=session_id
                )

            # Inspect refreshed financial state after auto-propagation of changes
            snapshot = self._graph.get_state(config)
            if snapshot.next and "request_financial_approval" in snapshot.next:
                fin_v2 = snapshot.values["financial_estimation"]
                req_v2 = snapshot.values["requirements"]
                tech_v2 = snapshot.values["technical_architecture"]

                print(f"\n--> Interrupt Triggered: Revised Proposal Approval Requested")
                print(f"    Requirements Version: v{req_v2['version']}")
                print(f"    Technical Version: v{tech_v2['version']} (Input Req v{tech_v2['requirements_version']})")
                print(
                    f"    Financial Version: v{fin_v2['version']} (Input Tech v{fin_v2['technical_proposal_version']})")
                print(f"    New Total: ${fin_v2['total']} {fin_v2['currency']}")

                # Final Approval
                print("\n--- User Approves Financial Proposal ---")
                final_state = self._graph.invoke(
                    Command(resume={"action": UserApprovalAction.APPROVE.value}),
                    config=config
                )

                print(f"\n=== Workflow Complete ===")
                print(f"Final Status: {final_state['status']}")
                print(
                    f"Requirements v{final_state['requirements']['version']} -> Tech v{final_state['technical_architecture']['version']} -> Financial v{final_state['financial_estimation']['version']}")

    def draw_workflow(self):
        self._graph.get_graph().draw_mermaid_png(output_file_path="techdoc_workflow.png")