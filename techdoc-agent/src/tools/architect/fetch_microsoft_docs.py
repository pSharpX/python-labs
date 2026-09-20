from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

from tools.mcp.microsoft_client import MicrosoftLearnClient


class MicrosoftDocsFetchInput(BaseModel):
    url: str = Field(
        description="Microsoft Learn article URL to retrieve."
    )

class FetchMicrosoftDocsTool(BaseTool):
    name: str = "fetch_microsoft_doc"
    description: str = (
        "Fetch a complete Microsoft Learn article after "
        "a relevant document has been identified."
    )

    args_schema: type[BaseModel] = MicrosoftDocsFetchInput

    __client: MicrosoftLearnClient

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.__client = MicrosoftLearnClient()

    async def _arun(
        self,
        url: str,
        **kwargs: Any,
    ) -> Any:

        return await self.__client.call_tool(
            "microsoft_docs_fetch",
            {
                "url": url,
            },
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(
            "Use async execution."
        )