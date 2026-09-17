from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from agents import TechDocReqScoutAgent
from config import langfuse_handler
from constants import AnalysisStatus
from prompts import TECH_ARCHITECT_SYSTEM_PROMPT, FINANCIAL_ESTIMATOR_SYSTEM_PROMPT
from settings import BaseModelSettings
from state import TechDocBuilderState, TechDocBuilderInput, TechDocBuilderOutput, TechDocReqScoutState
from tools import SaveMarkdownTool

AgentNodeType = Literal["requirements_scout_node", "tech_architect_node", "financial_estimator_node"]


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
            #input_schema=TechDocBuilderInput,
            input_schema=TechDocReqScoutState,
            output_schema=TechDocBuilderOutput,
            state_schema=TechDocBuilderState,
        )
        self.__tool = SaveMarkdownTool()

        self.__tech_architect_prompt = SystemMessage(content=TECH_ARCHITECT_SYSTEM_PROMPT)
        self.__financial_estimator_prompt = SystemMessage(content=FINANCIAL_ESTIMATOR_SYSTEM_PROMPT)

        self.__req_scout_agent = TechDocReqScoutAgent()

        self.graph = self.__build()

    @staticmethod
    def __pick_retriever(state: TechDocBuilderState) -> AgentNodeType:
        """Requirements-scout Node capture business requirements, objectives and define acceptance criteria."""

        status: AnalysisStatus = state["status"]

        if status == "ready_for_architecture":
            return "tech_architect_node"
        return "requirements_scout_node"

    def __tech_architect_node(self, state: TechDocBuilderState):
        """Technical Architect Node design and implement the technical solution based on functional requirements."""

        print("="*120)
        print(">> TECH ARCHITECT STATE")
        print("=" * 120)
        print(state)
        user_message = HumanMessage(state["requirements"])
        messages = [
            self.__tech_architect_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "technical_document": res.content,
        }

    def __financial_estimator_node(self, state: TechDocBuilderState):
        """Financial Estimator Node calculate the effort, the cost and commercial conditions."""

        user_message = HumanMessage(state["technical_document"])
        messages = [
            self.__financial_estimator_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "financial_document": res.content,
        }

    def __aggregator_node(self, state: TechDocBuilderState):
        """Aggregator Node collect all the document pieces and prepare the final document proposal."""

        requirements = state["requirements"]
        technical_document = state["technical_document"]
        financial_document = state["financial_document"]
        output = f"""
        [REQUIREMENTS]
        {requirements}
        [TECHNICAL DOCUMENT]
        {technical_document}
        [FINANCIAL DOCUMENT]
        {financial_document}
        """
        self.__tool._run(requirements, "requirements.md")
        self.__tool._run(technical_document, "technical_document.md")
        self.__tool._run(financial_document, "financial_document.md")
        return {
            "raw_document_content": output,
            "final_document": output
        }

    def __build(self):
        self.__builder.add_node("requirements_scout_node", self.__req_scout_agent.unwrap())
        self.__builder.add_node("tech_architect_node", self.__tech_architect_node)
        self.__builder.add_node("financial_estimator_node", self.__financial_estimator_node)
        self.__builder.add_node("aggregator_node", self.__aggregator_node)

        self.__builder.add_edge(START, "requirements_scout_node")

        self.__builder.add_conditional_edges("requirements_scout_node", self.__pick_retriever)

        self.__builder.add_edge("tech_architect_node", "financial_estimator_node")
        self.__builder.add_edge("financial_estimator_node", "aggregator_node")
        self.__builder.add_edge("aggregator_node", END)

        return self.__builder.compile(checkpointer=InMemorySaver())

    def invoke(self, question: str, input_obj: dict, session_id: str) -> TechDocBuilderOutput:
        return self.graph.invoke(
            input={
                "user_request": input_obj.get("user_request", ""),
                "messages": [
                    HumanMessage(content=question)
                ],
                "resources": input_obj.get("resources", []),
            },
            config={
                "callbacks": [langfuse_handler],
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