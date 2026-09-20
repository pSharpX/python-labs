from typing import Any


class MCPToolRegistry:

    def __init__(self, client):
        self.client = client
        self._tools: dict[str, Any] = {}

    async def refresh(self) -> None:

        tools = await self.client.list_tools()

        self._tools = {
            tool.name: tool
            for tool in tools
        }

    def has(self, name: str) -> bool:
        return name in self._tools

    def get(self, name: str) -> Any:

        if name not in self._tools:
            raise KeyError(
                f"MCP tool not available: {name}"
            )

        return self._tools[name]