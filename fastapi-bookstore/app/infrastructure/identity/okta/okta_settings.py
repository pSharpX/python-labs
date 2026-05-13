
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OktaSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="okta_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    org_url: str = Field(max_length=200, min_length=2)
    token: str = Field(max_length=200, min_length=2)
