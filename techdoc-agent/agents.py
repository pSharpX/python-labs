import warnings

from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from prompts import REQ_SCOUT_SYSTEM_PROMPT
from settings import BaseModelSettings
from state import TechDocReqScoutState
from tools import get_analysis_status, add_functional_risk, add_integration, update_scope, add_process, add_actor, \
    add_client_question, add_missing_information, add_assumption, update_functional_requirement

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"pydantic\..*",
)

requirement_scout_tools = [
    update_functional_requirement,
    add_assumption,
    add_missing_information,
    add_client_question,
    add_actor,
    add_process,
    update_scope,
    add_functional_risk,
    add_integration,
    get_analysis_status,
]

class TechDocReqScoutAgent:
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
        self.__system_prompt = REQ_SCOUT_SYSTEM_PROMPT
        self.__agent = create_agent(
            model=self.__model,
            tools=requirement_scout_tools,
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
            state_schema=TechDocReqScoutState,
            checkpointer=InMemorySaver()
        )

    def unwrap(self):
        return self.__agent

