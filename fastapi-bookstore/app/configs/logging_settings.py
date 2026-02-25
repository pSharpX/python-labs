from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class LoggingSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="log_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    level: str = Field()
    format: str = Field("text", alias="log_format") # when alias set env_prefix will be ignored.

settings = LoggingSettings()