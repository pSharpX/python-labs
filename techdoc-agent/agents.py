import warnings

from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import langfuse_handler
from prompts import TECHDOC_SYSTEM_PROMPT
from settings import BaseModelSettings
from tools import SaveMarkdownTool

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"pydantic\..*",
)


class TechDocState(AgentState):
    user_id: str


class TechDocAgent:
    def __init__(self):
        self.__model_settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__model_settings.model_name,
            model_provider=self.__model_settings.provider,
            temperature=self.__model_settings.temperature,
        )
        self.__system_prompt = TECHDOC_SYSTEM_PROMPT
        # noinspection bad-argument-type
        self.__agent = create_agent(
            model=self.__model,
            tools=[
                SaveMarkdownTool()
            ],
            system_prompt=self.__system_prompt,
            middleware=[
            ],
            name="techdoc-agent",
            state_schema=TechDocState,
            checkpointer=InMemorySaver()
        )

    def unwrap(self):
        return self.__agent

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to TechDoc Agent, your technical and functional proposal docs builder!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.__agent.invoke(
                input={
                    "user_id": input_obj["user_id"],
                    "messages": [HumanMessage(content=question)]
                },
                config={
                    "callbacks": [langfuse_handler],
                    "metadata": {
                        "langfuse_user_id": input_obj["user_id"],
                        "langfuse_session_id": session_id,
                        "langfuse_tags": ["environment:dev", "framework:langchain", "application:presales-assistant-agent", "component:techdoc-agent"]
                    },
                    "configurable": {
                        "thread_id": session_id
                    }
                },
                context=input_obj,
            )
            print(state["messages"][-1].content)
