from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[0]

class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GEMINI = "google_genai"
    GOOGLE_VERTEX = "google_vertex"

class LangFuseSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="langfuse_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    base_url: str = Field("http://localhost:3000", max_length=300, min_length=5)
    public_key: str = Field(max_length=100, min_length=2)
    secret_key: str = Field(max_length=100, min_length=2)

class BaseModelSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="model_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    provider: str = Field("openai", max_length=200, min_length=5)
    model_name: str = Field("gpt-3.5-turbo", alias="model_name", max_length=200, min_length=5)
    temperature: float = Field(0.2)
    max_tokens: int = Field(1000)
    verbose: bool = Field(False)

    @field_validator('provider', mode='after')
    @classmethod
    def validate_provider(cls, value: str) -> str:
        is_valid = value in (member.value for member in ModelProvider)
        if not is_valid:
            raise ValueError('Invalid model provider value')
        return value

class DatabaseSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="db_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    checkpoint_backend: str = Field("memory", max_length=20, min_length=1)
    checkpoint_url: str = Field("localhost", max_length=200, min_length=1)
    url: str = Field(max_length=200, min_length=5)
    username: str = Field(max_length=20, min_length=2, alias="db_user")
    password: str = Field(max_length=20, min_length=2, alias="db_pass")
    database_name: str = Field(max_length=50, min_length=2, alias="db_name")

class AuthSettings(BaseModel, case_sensitive=False):
    mode: Literal["dev", "api_key"] = "dev"
    dev_default_user: str = "dev-user"
    # api_key mode: {"<api key>": "<user id>"}; supply via env as JSON.
    api_keys: dict[str, str] = Field(default_factory=dict)
    admin_users: list[str] = Field(default_factory=list)

class ApplicationSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="app_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    owner: str = Field("utec-labs", max_length=100, min_length=1)
    name: str = Field("techdoc-builder-workflow", max_length=100, min_length=1)
    component: str = Field("builder-workflow", max_length=100, min_length=1)
    tags: list[str] = []

    app_name: str = "Technical Proposal Builder API"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8501"])
    log_level: str = "INFO"
    log_json: bool = True

    validation_rules_file: Path = BACKEND_ROOT / "config" / "validation_rules.json"
    rate_card_file: Path = BACKEND_ROOT / "config" / "rates.sample.json"
    rules_file: Path = BACKEND_ROOT / "config" / "financial_rules.sample.json"
    documents_output_dir: Path = BACKEND_ROOT / "docs" / "output"

    auth: AuthSettings = Field(default_factory=AuthSettings)

class DocumentSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="doc_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    company_name: str = Field("Your Company", max_length=100, min_length=1)
    primary_color: str = Field("1F3A5F", max_length=100, min_length=1)
    accent_color: str = Field("2E86AB", max_length=100, min_length=1)
    font_name: str = Field("Calibri", max_length=50, min_length=1)
    logo_path: Path | None = None
    footer_text: str = Field("Confidential — prepared for the named customer only", max_length=1000, min_length=1)

@lru_cache
def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings()

@lru_cache
def get_settings() -> ApplicationSettings:
    return ApplicationSettings()