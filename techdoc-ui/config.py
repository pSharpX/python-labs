"""Frontend configuration (environment variables or .env)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class FrontendSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="PS_", extra="ignore")

    api_base_url: str = "http://localhost:8000"
    api_timeout_seconds: float = 30.0
    # Auth: dev mode sends X-User-Id; api_key mode sends Authorization: Bearer <key>
    auth_mode: str = "dev"
    user_id: str = "dev-user"
    api_key: SecretStr | None = None

    poll_interval_seconds: float = 1.5
    poll_timeout_seconds: float = 300.0
    app_title: str = "Proposal Studio"
    company_name: str = "Your Company"


@lru_cache
def get_settings() -> FrontendSettings:
    return FrontendSettings()
