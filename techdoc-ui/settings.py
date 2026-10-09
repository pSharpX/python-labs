from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="app_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    backend_url: str = Field(max_length=200, min_length=5)

