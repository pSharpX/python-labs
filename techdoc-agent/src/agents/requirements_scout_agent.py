from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import serde
from settings import BaseModelSettings
from src.prompts import REQUIREMENTS_SYSTEM_PROMPT
from src.state.requirements import RequirementsOutputSchema


tools = []

class RequirementsScoutAgent:
    """
    Agente especializado en el levantamiento y análisis de requerimientos.

    Identifica y estructura las necesidades del cliente, transforma los
    requerimientos en objetivos de negocio claros y establece criterios
    de aceptación verificables.

    Su propósito es construir un brief funcional completo que sirva como
    base para las siguientes etapas del proceso de preventa.
    """
    def __init__(self):
        self.__model_settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__model_settings.model_name,
            model_provider=self.__model_settings.provider,
            temperature=self.__model_settings.temperature,
        )
        self.__system_prompt = REQUIREMENTS_SYSTEM_PROMPT
        self.__agent = create_agent(
            model=self.__model,
            tools=tools,
            system_prompt=self.__system_prompt,
            middleware=[
                #CustomGuardsMiddleware(),
                #PIIMiddleware("api_key", detector=r"sk-[a-zA-Z0-9]{32}", strategy="block"),
                #PIIMiddleware("credit_card", strategy="mask"),
                #PIIMiddleware("email", strategy="redact"),
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
            ],
            name="techdoc-reqscout-agent",
            response_format=RequirementsOutputSchema,
            checkpointer=InMemorySaver(serde=serde)
        )

    def run(self, raw_requirements: str, config) -> RequirementsOutputSchema:
        result = self.__agent.invoke({
            "messages": [
                HumanMessage(content=raw_requirements)
            ]
        }, config={
            "configurable": {
                "thread_id": config["thread_id"]
            }
        })
        return result["structured_response"]

    async def arun(self, raw_requirements: str, config) -> RequirementsOutputSchema:
        result = await self.__agent.ainvoke({
            "messages": [
                HumanMessage(content=raw_requirements)
            ]
        }, config={
            "configurable": {
                "thread_id": config["thread_id"]
            }
        })
        return result["structured_response"]

    def unwrap(self):
        return self.__agent

