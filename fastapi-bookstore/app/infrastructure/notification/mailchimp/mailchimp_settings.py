
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MailchimpSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="mailchimp_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    base_url: str = Field(max_length=200, min_length=2)
    api_key: str = Field(max_length=200, min_length=2)
    merge_language: str = Field("handlebars", max_length=200, min_length=2)
