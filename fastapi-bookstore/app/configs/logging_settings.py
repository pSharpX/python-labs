from enum import Enum
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class LogFormat(str, Enum):
    JSON = "json"
    TEXT = "text"

class LoggingSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="log_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    level: str = Field()
    format: str = Field("text", alias="log_format") # when alias set env_prefix will be ignored.

    @field_validator('format', mode='after')
    @classmethod
    def validate_format(cls, value: str) -> str:
        is_valid = value in (member.value for member in LogFormat)
        if not is_valid :
            raise ValueError('Invalid log format value')
        return value
