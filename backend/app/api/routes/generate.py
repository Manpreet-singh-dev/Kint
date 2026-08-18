"""Code generation API endpoints."""

from fastapi import APIRouter, Depends, status
from app.api.deps import get_coder_service
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.coder import CoderService

router = APIRouter(tags=["Code Generation"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Application Files",
    description="Generate a complete web application (HTML, CSS, JS) from a natural language prompt using Claude.",
    responses={
        400: {
            "description": "Bad Request or Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "CodeGenerationError",
                        "message": "Generated code must include an index.html file as the entry point.",
                        "detail": "Generated code must include an index.html file as the entry point.",
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error or Configuration Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "ConfigurationError",
                        "message": "ANTHROPIC_API_KEY environment variable not set.",
                        "detail": "ANTHROPIC_API_KEY environment variable not set.",
                    }
                }
            },
        },
    },
)
def generate_application(
    request: GenerateRequest,
    coder_service: CoderService = Depends(get_coder_service),
) -> GenerateResponse:
    """
    Generate an app from a text prompt using the Coder agent.

    Phase 1: Single-agent implementation - Coder agent generates files directly.
    Phase 2 will add: Planner → Coder → Sandbox → Debugger pipeline with retry logic.
    """
    files = coder_service.generate_files(request.prompt)

    return GenerateResponse(
        message=f"Generated {len(files)} file(s) based on your prompt. Preview coming in next task!",
        files=files,
        preview_url=None,  # Connected in sandbox execution workflow
    )
