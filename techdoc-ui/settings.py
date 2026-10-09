from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class ApplicationSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="app_", env_file=".env", env_file_encoding="utf-8", extra="allow")


