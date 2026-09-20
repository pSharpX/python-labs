from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

from tools.mcp.microsoft_client import MicrosoftLearnClient


class MicrosoftDocsFetchInput(BaseModel):
    url: str = Field(
        description="URL del artículo de Microsoft Learn que se desea consultar."
    )

class FetchMicrosoftDocsTool(BaseTool):
    name: str = "obtener_documentacion_microsoft"
    description: str = (
        "Obtiene el contenido completo de un artículo "
        "de Microsoft Learn previamente identificado. "
        "Utiliza esta herramienta cuando necesites "
        "revisar en detalle una documentación técnica "
        "antes de tomar una decisión arquitectónica."
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