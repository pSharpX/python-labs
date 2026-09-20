from __future__ import annotations

from typing import Any

from fastmcp import Client


class FastMCPHttpClient:
    """
    Async client for a FastMCP server exposed through
    Streamable HTTP.
    """

    def __init__(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
    ):
        self.url = url
        self.headers = headers or {}

    async def list_tools(self) -> list[Any]:
        async with Client(
            self.url,
            headers=self.headers,
        ) as client:
            result = await client.list_tools()
            return result

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:

        async with Client(
            self.url,
            headers=self.headers,
        ) as client:

            return await client.call_tool(
                tool_name,
                arguments or {},
            )