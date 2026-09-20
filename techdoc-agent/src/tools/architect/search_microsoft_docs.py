from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

from tools.mcp.microsoft_client import MicrosoftLearnClient


class MicrosoftDocsSearchInput(BaseModel):
    query: str = Field(
        description=(
            "Technical question or concept to search "
            "in official Microsoft Learn documentation."
        )
    )

class SearchMicrosoftDocsTool(BaseTool):
    name: str = "search_microsoft_docs"
    description: str = (
        "Search official Microsoft Learn documentation. "
        "Use this when evaluating Microsoft technologies, "
        "Azure services, .NET, Microsoft identity, networking, "
        "security, architecture patterns, or Microsoft cloud services."
    )
    args_schema: type[BaseModel] = MicrosoftDocsSearchInput

    __client: MicrosoftLearnClient

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.__client = MicrosoftLearnClient()

    async def _arun(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        return await self.__client.call_tool(
            "microsoft_docs_search",
            {
                "query": query,
            },
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(
            "Use async execution."
        )