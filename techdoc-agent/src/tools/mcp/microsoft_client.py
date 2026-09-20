
from .client import FastMCPHttpClient


class MicrosoftLearnClient(FastMCPHttpClient):

    def __init__(
        self,
        url: str = "https://learn.microsoft.com/api/mcp",
    ):
        super().__init__(url)