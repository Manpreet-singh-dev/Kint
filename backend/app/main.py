"""
FastAPI application entry point.

Initializes the FastAPI application, CORS middleware, global exception handlers,
and registers API routes according to the Auth0 FastAPI best practices guide.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    """Application factory for FastAPI instance."""
    settings = get_settings()

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend API for AI App Builder - Multi-agent web application generator.",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Domain exception handlers
    register_exception_handlers(application)

    # Include routes at root level (ensuring backwards compatibility with frontend)
    application.include_router(api_router)

    # Also mount under /api/v1 for RESTful versioning
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_app()
