
from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from rich import print

from config import langfuse_handler
from prompts import SYSTEM_PROMPT
from settings import BaseModelSettings


class ProductAssistantState(AgentState):
    first_product: str
    second_product: str


class RAGPoweredAgent:
    def __init__(self, model_settings: BaseModelSettings, tools: list):
        self.model_settings = model_settings
        self.model = init_chat_model(
            model=self.model_settings.model_name,
            model_provider=self.model_settings.provider,
            temperature=self.model_settings.temperature,
            max_tokens=self.model_settings.max_tokens,
        )
        # noinspection bad-argument-type
        self.agent = create_agent(
            model=self.model,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            name="smarty-scraper-agent",
            checkpointer=InMemorySaver(),
            state_schema=ProductAssistantState,
        )

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to Product Assistant Agent!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.agent.invoke(
                input={
                    "first_product": input_obj["first_product"],
                    "second_product": input_obj["second_product"],
                    "messages": [HumanMessage(content=question)]
                },
                config={
                    "callbacks": [langfuse_handler],
                    "metadata": {
                        "langfuse_user_id": input_obj["user_id"],
                        "langfuse_session_id": session_id,
                        "langfuse_tags": ["environment:dev", "framework:langchain", "application:smarty-scraper-agent"],
                    },
                    "configurable": {
                        "thread_id": session_id
                    }
                },
                context=input_obj,
            )
            print(state["messages"][-1].content)

