
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MainSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    identity_provider: str = Field("okta", alias="auth_provider") # when alias set env_prefix will be ignored.
    notification_provider: str = Field("mailchimp")
