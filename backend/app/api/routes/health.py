"""Health check API endpoints."""

from fastapi import APIRouter
from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the operational status and version of the API service.",
)
@router.get(
    "/",
    response_model=HealthResponse,
    summary="Root Health Check",
    description="Root endpoint providing service health status.",
)
def check_health() -> HealthResponse:
    """Return current service health and metadata."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
    )
