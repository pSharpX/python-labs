import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import serde
from settings import BaseModelSettings
from src.prompts import ARCHITECT_SYSTEM_PROMPT
from src.state.architect import TechArchitectAgentState, TechArchitectOutputSchema
from src.tools.architect import update_technical_document
from src.tools.mcp import MCPSettings, MCPToolsAdapter


class TechArchitectAgent:
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
    def __init__(self, mcp_adapter: MCPToolsAdapter):
        self.__model_settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__model_settings.model_name,
            model_provider=self.__model_settings.provider,
            temperature=self.__model_settings.temperature,
        )
        self.__system_prompt = ARCHITECT_SYSTEM_PROMPT

        self.__mcp_settings = MCPSettings()
        self.__mcp_adapter = mcp_adapter
        tools = self.__mcp_adapter.get_tools(
            allowed_tools=self.__mcp_settings.allowed_tools
        )

        self.__agent = create_agent(
            model=self.__model,
            tools=tools.extend([
                update_technical_document
            ]),
            system_prompt=self.__system_prompt,
            name="techdoc-architect-agent",
            state_schema=TechArchitectAgentState,
            checkpointer=InMemorySaver(serde=serde)
        )

    def run(self, requirements: dict) -> TechArchitectOutputSchema:
        prompt = "Crea la propuesta técnico-funcional a partir de estos requisitos estructurados..\n\n" + json.dumps(
            requirements, default=str, ensure_ascii=False)
        result = self.__agent.invoke({
            "messages": [
                HumanMessage(content=prompt)
            ]
        })
        return result["structured_response"]

    async def arun(self, requirements: dict) -> TechArchitectOutputSchema:
        prompt = "Crea la propuesta técnico-funcional a partir de estos requisitos estructurados..\n\n" + json.dumps(
            requirements, default=str, ensure_ascii=False)
        result = await self.__agent.ainvoke({
            "messages": [
                HumanMessage(content=prompt)
            ]
        })
        return result["structured_response"]
    
    def unwrap(self):
        return self.__agent

