from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

from tools.mcp.microsoft_client import MicrosoftLearnClient


class MicrosoftDocsSearchInput(BaseModel):
    query: str = Field(
        description=(
            "Pregunta técnica o concepto que se desea buscar"
            " en la documentación oficial de Microsoft Learn."
        )
    )

class SearchMicrosoftDocsTool(BaseTool):
    name: str = "buscar_documentacion_microsoft"
    description: str = (
        "Busca información técnica actualizada "
        "en la documentación oficial de Microsoft Learn. "
        "Utiliza esta herramienta para investigar "
        "servicios de Azure, Microsoft .NET, identidad, "
        "seguridad, integración, arquitectura y otras "
        "tecnologías de Microsoft. "
        "Debe utilizarse cuando la respuesta dependa "
        "de documentación técnica específica o actualizada."
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