"""
Domain-specific exceptions and global exception handlers.

Decouples internal application errors from HTTP presentation logic,
following the pattern recommended in the Auth0 FastAPI best practices guide.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppBuilderException(Exception):
    """Base exception for all domain-specific errors in AI App Builder."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CodeGenerationError(AppBuilderException):
    """Raised when code generation via LLM fails or returns invalid output."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, status_code=status_code)


class SandboxExecutionError(AppBuilderException):
    """Raised when execution in E2B sandbox fails or credentials are missing."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message=message, status_code=status_code)


class ConfigurationError(AppBuilderException):
    """Raised when required configuration or API keys are missing."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message=message, status_code=status_code)


async def app_builder_exception_handler(request: Request, exc: AppBuilderException) -> JSONResponse:
    """Handle domain-specific AppBuilderException errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "detail": exc.message,  # detail for backwards-compatibility with FastAPI client conventions
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom domain exception handlers on the FastAPI application."""
    app.add_exception_handler(AppBuilderException, app_builder_exception_handler)
    app.add_exception_handler(CodeGenerationError, app_builder_exception_handler)
    app.add_exception_handler(SandboxExecutionError, app_builder_exception_handler)
    app.add_exception_handler(ConfigurationError, app_builder_exception_handler)
