from .fastmcp_client import FastMCPHttpClient


class AWSMCPClient(FastMCPHttpClient):

    def __init__(
        self,
        url: str = "https://aws-mcp.us-east-1.api.aws/mcp",
    ):
        super().__init__(url)