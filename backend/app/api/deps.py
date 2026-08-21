"""
Dependency injection providers for FastAPI endpoints.

Follows the Dependency Injection pattern from the Auth0 FastAPI best practices guide.
"""

from fastapi import Depends
from app.core.config import Settings, get_settings
from app.services.coder import CoderService
from app.services.debugger import DebuggerService
from app.services.planner import PlannerService
from app.services.sandbox import SandboxService
from app.services.providers import LLMProvider, get_llm_provider


def get_app_settings() -> Settings:
    """Provide application settings instance."""
    return get_settings()


def get_provider(settings: Settings = Depends(get_app_settings)) -> LLMProvider:
    """Provide the configured LLM provider (Claude, Gemini, Grok, Groq)."""
    return get_llm_provider(settings)


def get_planner_service(provider: LLMProvider = Depends(get_provider)) -> PlannerService:
    """Provide PlannerService instance with injected LLM provider."""
    return PlannerService(provider=provider)


def get_coder_service(provider: LLMProvider = Depends(get_provider)) -> CoderService:
    """Provide CoderService instance with injected LLM provider."""
    return CoderService(provider=provider)


def get_debugger_service(provider: LLMProvider = Depends(get_provider)) -> DebuggerService:
    """Provide DebuggerService instance with injected LLM provider."""
    return DebuggerService(provider=provider)


def get_sandbox_service(settings: Settings = Depends(get_app_settings)) -> SandboxService:
    """Provide SandboxService instance with injected settings."""
    return SandboxService(settings=settings)
