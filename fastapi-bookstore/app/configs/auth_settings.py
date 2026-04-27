
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="auth_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    provider: str = Field("ad", alias="auth_provider") # when alias set env_prefix will be ignored.
