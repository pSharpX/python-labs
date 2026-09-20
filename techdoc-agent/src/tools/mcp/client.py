from typing import Any, Protocol


class MCPClient(Protocol):

    async def list_tools(self) -> list[Any]:
        pass

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        pass