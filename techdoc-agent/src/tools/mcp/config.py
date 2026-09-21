from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="mcp_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    techdoc_url: str = Field("http://localhost:8000/mcp", max_length=1000, min_length=5)
    microsoft_learn_url: str = Field("https://learn.microsoft.com/api/mcp", max_length=1000, min_length=5)
    aws_url: str = Field("https://aws-mcp.us-east-1.api.aws/mcp", max_length=1000, min_length=5)

    allowed_tools: list[str] = []
    #azure_url: str = Field("", max_length=1000, min_length=5)
