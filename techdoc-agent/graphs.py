import operator
from typing import Annotated, TypedDict, Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from config import langfuse_handler
from prompts import TECHDOC_SYSTEM_PROMPT, ORCHESTRATOR_SYSTEM_PROMPT, REQ_SCOUT_SYSTEM_PROMPT, \
    TECH_ARCHITECT_SYSTEM_PROMPT, FINANCIAL_ESTIMATOR_SYSTEM_PROMPT
from settings import BaseModelSettings
from tools import SaveMarkdownTool


class TechDocGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class TechDocGraphAgent:
    """A langgraph powered assistant that transforms functional requirements into structured technical proposal."""

    def __init__(self):
        self.__settings = BaseModelSettings()
        self.__system_prompt = SystemMessage(content=TECHDOC_SYSTEM_PROMPT)
        self.__tools = [
            SaveMarkdownTool()
        ]
        self.__tools_by_name = {tool.name: tool for tool in self.__tools}
        self.__model = init_chat_model(
            model=self.__settings.model_name,
            model_provider=self.__settings.provider,
            temperature=self.__settings.temperature,
        ).bind_tools(self.__tools)
        self.__builder = StateGraph(TechDocGraphState)
        self.graph = self.__build()

    def __llm_call(self, state: TechDocGraphState):
        """LLM decides whether to call a tool or not"""
        messages = [
            self.__system_prompt,
            *state["messages"]
        ]

        return { "messages": [self.__model.invoke(messages)] }

    def __tool_node(self, state: TechDocGraphState):
        """Perform the tool call"""

        result = []
        for tool_call in state["messages"][-1].tool_calls:
            selected_tool = self.__tools_by_name[tool_call["name"]]
            tool_output = selected_tool.invoke(tool_call["args"])
            result.append(
                ToolMessage(
                    content=tool_output,
                    tool_call_id=tool_call["id"]
                )
            )

        return { "messages": result }

    @staticmethod
    def __should_continue(state: TechDocGraphState) -> Literal["tool_node", END]:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

        messages = state["messages"]
        last_message = messages[-1]

        # If LLM makes a tool call, then perform an action
        if last_message.tool_calls:
            return "tool_node"

        # Otherwise, we stop (reply to the user)
        return END

    def __build(self):
        self.__builder.add_node("llm_call", self.__llm_call)
        self.__builder.add_node("tool_node", self.__tool_node)

        self.__builder.add_edge(START, "llm_call")
        self.__builder.add_conditional_edges("llm_call", self.__should_continue, ["tool_node", END])
        self.__builder.add_edge("tool_node", "llm_call")

        return self.__builder.compile(checkpointer=InMemorySaver())

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to TechDoc Agent, your technical and functional proposal docs builder!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.graph.invoke(
                input={
                    "messages": [HumanMessage(content=question)]
                },
                config={
                    "callbacks": [langfuse_handler],
                    "metadata": {
                        "langfuse_user_id": input_obj["user_id"],
                        "langfuse_session_id": session_id,
                        "langfuse_tags": ["environment:dev", "framework:langchain", "application:presales-assistant-agent", "component:techdoc-graph-agent"]
                    },
                    "configurable": {
                        "thread_id": session_id
                    }
                })
            print(state["messages"][-1].content)


AgentNodeType = Literal["requirements_scout_node", "tech_architect_node", "financial_estimator_node"]

class OrchestratorAgentState(TypedDict):
    user_query: str
    messages: Annotated[list[AnyMessage], operator.add]
    next_agent: AgentNodeType
    requirements: str
    technical_document: str
    financial_document: str


class OrchestratorAgent:
    """A langgraph powered orchestrator agent that route and delegate requirements to subagents."""

    def __init__(self):
        self.__settings = BaseModelSettings()
        self.__system_prompt = SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT)
        self.__tools = [
            SaveMarkdownTool()
        ]
        self.__tools_by_name = {tool.name: tool for tool in self.__tools}
        self.__model = init_chat_model(
            model=self.__settings.model_name,
            model_provider=self.__settings.provider,
            temperature=self.__settings.temperature,
        ).bind_tools(self.__tools)
        self.__builder = StateGraph(OrchestratorAgentState)

        self.__req_scout_prompt = SystemMessage(content=REQ_SCOUT_SYSTEM_PROMPT)
        self.__tech_architect_prompt = SystemMessage(content=TECH_ARCHITECT_SYSTEM_PROMPT)
        self.__financial_estimator_prompt = SystemMessage(content=FINANCIAL_ESTIMATOR_SYSTEM_PROMPT)

        self.graph = self.__build()

    def __router_node(self, state: OrchestratorAgentState):
        """LLM decides which subagent should go next"""

        user_message = HumanMessage(state["user_query"])
        messages = [
            self.__system_prompt,
            *state["messages"],
            user_message,
        ]
        res = self.__model.invoke(messages)
        print(res)
        return {
            "next_agent": res.content,
            "messages": [user_message, res],
        }

    @staticmethod
    def __pick_retriever(state: OrchestratorAgentState) -> AgentNodeType:
        """Retriever decides which subagent handle and process user query."""

        next_agent = state["next_agent"]
        if next_agent == "REQUIREMENTS_SCOUT":
            return "requirements_scout_node"
        elif next_agent == "TECH_ARCHITECT":
            return "tech_architect_node"
        elif next_agent == "FINANCIAL_ESTIMATOR":
            return "financial_estimator_node"
        return END

    def __requirements_scout_node(self, state: OrchestratorAgentState):
        """Requirements-scout Node capture business requirements, objectives and define acceptance criteria."""

        user_message = HumanMessage(state["user_query"])
        messages = [
            self.__req_scout_prompt,
            *state["messages"],
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "requirements": res.content,
            #"messages": [user_message, res],
        }

    def __tech_architect_node(self, state: OrchestratorAgentState):
        """Technical Architect Node design and implement the technical solution based on functional requirements."""

        user_message = HumanMessage(state["requirements"])
        messages = [
            self.__tech_architect_prompt,
            *state["messages"],
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "technical_document": res.content,
            #"messages": [user_message, res],
        }

    def __financial_estimator_node(self, state: OrchestratorAgentState):
        """Financial Estimator Node calculate the effort, the cost and commercial conditions."""

        user_message = HumanMessage(state["technical_document"])
        messages = [
            self.__financial_estimator_prompt,
            *state["messages"],
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "financial_document": res.content,
            #"messages": [user_message, res],
        }

    def __llm_call(self, state: OrchestratorAgentState):
        """LLM decides whether to call a tool or not"""
        messages = [
            self.__system_prompt,
            *state["messages"]
        ]

        return { "messages": [self.__model.invoke(messages)] }

    def __tool_node(self, state: OrchestratorAgentState):
        """Perform the tool call"""

        result = []
        for tool_call in state["messages"][-1].tool_calls:
            selected_tool = self.__tools_by_name[tool_call["name"]]
            tool_output = selected_tool.invoke(tool_call["args"])
            result.append(
                ToolMessage(
                    content=tool_output,
                    tool_call_id=tool_call["id"]
                )
            )

        return { "messages": result }

    @staticmethod
    def __should_continue(state: OrchestratorAgentState) -> Literal["tool_node", END]:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

        messages = state["messages"]
        last_message = messages[-1]

        # If LLM makes a tool call, then perform an action
        if last_message.tool_calls:
            return "tool_node"

        # Otherwise, we stop (reply to the user)
        return END

    def __build(self):
        self.__builder.add_node("router_node", self.__router_node)
        self.__builder.add_node("tool_node", self.__tool_node)
        self.__builder.add_node("pick_retriever", self.__pick_retriever)
        self.__builder.add_node("requirements_scout_node", self.__requirements_scout_node)
        self.__builder.add_node("tech_architect_node", self.__tech_architect_node)
        self.__builder.add_node("financial_estimator_node", self.__financial_estimator_node)

        self.__builder.add_edge(START, "router_node")
        self.__builder.add_conditional_edges("router_node", self.__pick_retriever)
        self.__builder.add_edge("requirements_scout_node", "tech_architect_node")
        self.__builder.add_edge("tech_architect_node", "financial_estimator_node")
        #self.__builder.add_edge("financial_estimator_node", END)

        self.__builder.add_conditional_edges("financial_estimator_node", self.__should_continue, ["tool_node", END])
        self.__builder.add_edge("tool_node", "router_node")

        return self.__builder.compile(checkpointer=InMemorySaver())

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to Orchestrator Agent, your helpful assistant!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.graph.invoke(
                input={
                    "user_query": question
                },
                config={
                    "callbacks": [langfuse_handler],
                    "metadata": {
                        "langfuse_user_id": input_obj["user_id"],
                        "langfuse_session_id": session_id,
                        "langfuse_tags": ["environment:dev", "framework:langchain", "application:presales-assistant-agent", "component:orchestrator-agent"]
                    },
                    "configurable": {
                        "thread_id": session_id
                    }
                })
            print(state["messages"][-1].content)


