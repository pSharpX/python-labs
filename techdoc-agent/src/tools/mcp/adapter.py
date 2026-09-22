import asyncio

from typing import List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from .config import MCPSettings


class MCPToolsAdapter:
    """
    Adaptador para descubrir y exponer como herramientas de LangChain
    las herramientas disponibles en múltiples servidores MCP.

    Los servidores MCP son configurados mediante MCPSettings. Las
    herramientas son descubiertas dinámicamente y no requieren wrappers
    específicos en el código de la aplicación.
    """

    def __init__(
            self,
            mcp_client: MultiServerMCPClient,
            discovered_tools: list[BaseTool],
    ):
        self.__mcp_client = mcp_client
        self.__discovered_tools = discovered_tools

    @classmethod
    async def acreate(cls, settings: MCPSettings) -> "MCPToolsAdapter":
        mcp_client = MultiServerMCPClient(
{
                "microsoft": {
                    "transport": "http",
                    "url": settings.microsoft_learn_url,
                },
                "aws": {
                    "transport": "http",
                    "url": settings.aws_url,
                },
                # "techdoc-mcp": {
                #     "transport": "http",
                #     "url": settings.techdoc_url,
                # },
            },
            tool_name_prefix=True,
        )
        discovered_tools = await mcp_client.get_tools()
        return cls(mcp_client, discovered_tools)

    @classmethod
    def create(cls, settings: MCPSettings) -> "MCPToolsAdapter":
        mcp_client = MultiServerMCPClient(
            {
                "microsoft": {
                    "transport": "http",
                    "url": settings.microsoft_learn_url,
                },
                "aws": {
                    "transport": "http",
                    "url": settings.aws_url,
                },
                # "techdoc-mcp": {
                #     "transport": "http",
                #     "url": settings.techdoc_url,
                # },
            },
            tool_name_prefix=True,
        )
        discovered_tools = asyncio.run(mcp_client.get_tools())
        # for tool in discovered_tools:
        #     print(f"MCP tool discovered: {tool.name}")
        return cls(mcp_client, discovered_tools)

    def get_tools(self, allowed_tools: list[str]) -> List[BaseTool]:
        selected_tools = [tool for tool in self.__discovered_tools if tool.name in allowed_tools]
        return selected_tools
