from .fastmcp_client import FastMCPHttpClient


class AzureMCPClient(FastMCPHttpClient):

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            url,
            headers=headers,
        )