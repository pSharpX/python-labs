import warnings

from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import langfuse_handler
from prompts import SYSTEM_PROMPT
from rich import print
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
        self.model_settings = BaseModelSettings()
        self.model = init_chat_model(
            model=self.model_settings.model_name,
            model_provider=self.model_settings.provider,
            temperature=self.model_settings.temperature,
        )
        self.system_prompt = SYSTEM_PROMPT
        # noinspection bad-argument-type
        self.agent = create_agent(
            model=self.model,
            tools=[
                SaveMarkdownTool()
            ],
            system_prompt=self.system_prompt,
            middleware=[
            ],
            name="techdoc-agent",
            state_schema=TechDocState,
            checkpointer=InMemorySaver()
        )

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to TechDoc Agent, your technical and functional proposal docs builder!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.agent.invoke(
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
