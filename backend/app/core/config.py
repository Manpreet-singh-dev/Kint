from enum import Enum
from functools import lru_cache
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderEnum(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    PROJECT_NAME: str = "AI App Builder"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS origins
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]

    # LLM provider selection
    LLM_PROVIDER: str = "claude"

    # Third-party API keys
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    E2B_API_KEY: str | None = None

    # Claude model settings
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 4096

    # Gemini model settings
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_MAX_TOKENS: int = 8192

    @field_validator("LLM_PROVIDER", mode="before")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        valid = [e.value for e in LLMProviderEnum]
        if v.lower() not in valid:
            raise ValueError(
                f"Invalid LLM_PROVIDER: '{v}'. Must be one of: {valid}"
            )
        return v.lower()

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=("backend/.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
