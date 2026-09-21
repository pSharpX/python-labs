from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from config import serde
from settings import BaseModelSettings
from src.prompts import ARCHITECT_SYSTEM_PROMPT
from src.state.requirements import TechDocReqScoutState
from src.tools.mcp import MCPToolsAdapter, MCPSettings


class TechDocArchitectAgent:
    """
    Agente especializado en arquitectura y diseño de soluciones tecnológicas.

    Analiza los requerimientos funcionales y no funcionales del cliente,
    identifica restricciones, dependencias, integraciones y necesidades
    técnicas, y propone una arquitectura de solución coherente con el
    contexto del negocio.

    Utiliza las herramientas técnicas disponibles, incluyendo herramientas
    proporcionadas por servidores MCP, para consultar documentación y
    capacidades actualizadas de las plataformas y servicios tecnológicos.

    Evalúa alternativas arquitectónicas, identifica trade-offs y documenta
    las decisiones técnicas, supuestos, riesgos y dependencias relevantes.

    Su propósito es transformar el brief de requerimientos en una propuesta
    técnica y arquitectónica que sirva como base para las siguientes etapas
    del proceso de preventa.
    """
    def __init__(self, mcp_tools_adapter: MCPToolsAdapter,):
        self.__model_settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__model_settings.model_name,
            model_provider=self.__model_settings.provider,
            temperature=self.__model_settings.temperature,
        )
        self.__system_prompt = ARCHITECT_SYSTEM_PROMPT
        self.__agent = create_agent(
            model=self.__model,
            tools=mcp_tools_adapter.get_tools(),
            system_prompt=self.__system_prompt,
            name="techdoc-architect-agent",
            state_schema=TechDocReqScoutState,
            checkpointer=InMemorySaver(serde=serde)
        )

    @classmethod
    async def create(cls, mcp_settings: MCPSettings, ) -> "TechDocArchitectAgent":
        mcp_tools_adapter = await MCPToolsAdapter.acreate(mcp_settings)

        return cls(mcp_tools_adapter=mcp_tools_adapter)

    def unwrap(self):
        return self.__agent

