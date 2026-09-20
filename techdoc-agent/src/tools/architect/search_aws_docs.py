from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

from tools.mcp.aws_client import AWSMCPClient


class SearchAWSDocsInput(BaseModel):
    query: str = Field(
        description=(
            "AWS architecture or service question. "
            "Examples: Lambda vs ECS, SQS vs SNS, "
            "API Gateway architecture, VPC design."
        )
    )

class SearchAWSDocsTool(BaseTool):
    name: str = "search_aws_docs"
    description: str = (
        "Search current official AWS documentation and "
        "architecture guidance. Use this when evaluating "
        "AWS services or AWS architecture."
    )

    args_schema: type[BaseModel] = SearchAWSDocsInput

    __client: AWSMCPClient

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.__client = AWSMCPClient()

    async def _arun(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:

        # Tool name should be discovered from tools/list
        # rather than permanently hardcoded.
        return await self.__client.call_tool(
            "search_documentation",
            {
                "query": query,
            },
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()