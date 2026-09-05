import operator
from typing import Annotated, TypedDict, Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from config import langfuse_handler
from prompts import SYSTEM_PROMPT
from settings import BaseModelSettings
from tools import SaveMarkdownTool


class TechDocGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class TechDocGraphAgent:
    """A langgraph powered assistant that transforms functional requirements into structured technical proposal."""

    def __init__(self):
        self.__settings = BaseModelSettings()
        self.__system_prompt = SystemMessage(content=SYSTEM_PROMPT)
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

