from .client import MCPClient
from .fastmcp_client import FastMCPHttpClient
from .microsoft_client import MicrosoftLearnClient
from .aws_client import AWSMCPClient
from .azure_client import AzureMCPClient


class MCPClientFactory:

    @staticmethod
    def local(url: str) -> MCPClient:
        return FastMCPHttpClient(url)

    @staticmethod
    def microsoft() -> MCPClient:
        return MicrosoftLearnClient()

    @staticmethod
    def aws(url: str) -> MCPClient:
        return AWSMCPClient(url)

    @staticmethod
    def azure(
        url: str,
        headers: dict[str, str] | None = None,
    ) -> MCPClient:
        return AzureMCPClient(
            url,
            headers=headers,
        )