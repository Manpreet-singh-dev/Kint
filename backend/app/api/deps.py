"""
Dependency injection providers for FastAPI endpoints.

Follows the Dependency Injection pattern from the Auth0 FastAPI best practices guide.
"""

from fastapi import Depends
from app.core.config import Settings, get_settings
from app.services.coder import CoderService
from app.services.sandbox import SandboxService


def get_app_settings() -> Settings:
    """Provide application settings instance."""
    return get_settings()


def get_coder_service(settings: Settings = Depends(get_app_settings)) -> CoderService:
    """Provide CoderService instance with injected settings."""
    return CoderService(settings=settings)


def get_sandbox_service(settings: Settings = Depends(get_app_settings)) -> SandboxService:
    """Provide SandboxService instance with injected settings."""
    return SandboxService(settings=settings)
