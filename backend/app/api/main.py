"""
Central API router combining all route modules.

Follows the Auth0 FastAPI structure pattern: `app/api/main.py`.
"""

from fastapi import APIRouter
from app.api.routes.generate import router as generate_router
from app.api.routes.health import router as health_router
from app.api.routes.sandbox import router as sandbox_router

api_router = APIRouter()

# Register route modules
api_router.include_router(health_router)
api_router.include_router(generate_router)
api_router.include_router(sandbox_router)
