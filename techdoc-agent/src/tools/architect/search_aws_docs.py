from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

from tools.mcp.aws_client import AWSMCPClient


class SearchAWSDocsInput(BaseModel):
    query: str = Field(
        description=(
            "Pregunta sobre arquitectura o servicios de AWS. "
            "Ejemplos: Lambda vs. ECS, SQS vs. SNS, arquitectura de API Gateway, diseño de VPC."
        )
    )

class SearchAWSDocsTool(BaseTool):
    name: str = "buscar_documentation_aws"
    description: str = (
        "Consulta información técnica actualizada "
        "de AWS para apoyar decisiones de arquitectura. "
        "Utiliza esta herramienta para investigar "
        "servicios, capacidades, patrones de arquitectura, "
        "limitaciones y buenas prácticas de AWS."
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