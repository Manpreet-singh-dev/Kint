"""Code generation API endpoints."""

from fastapi import APIRouter, Depends, status
from app.api.deps import get_coder_service, get_sandbox_service
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.coder import CoderService
from app.services.sandbox import SandboxService

router = APIRouter(tags=["Code Generation"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Application Files",
    description=(
        "Generate a complete web application from a natural language prompt "
        "using Claude, execute it in an E2B sandbox, and return a live preview URL."
    ),
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
async def generate_application(
    request: GenerateRequest,
    coder_service: CoderService = Depends(get_coder_service),
    sandbox_service: SandboxService = Depends(get_sandbox_service),
) -> GenerateResponse:
    """
    Generate an app from a text prompt and run it in a live sandbox.

    Pipeline: User Prompt → Coder Agent (Claude) → E2B Sandbox → Preview URL.
    Phase 1: Single-agent, no retry logic. Phase 2 adds Planner/Debugger loop.
    """
    # Step 1: Generate files via Claude
    files = coder_service.generate_files(request.prompt)

    # Step 2: Execute in E2B sandbox to get a live preview
    sandbox_result = await sandbox_service.execute_files(files)

    # Build the response message
    file_count = len(files)
    if sandbox_result.preview_url:
        message = (
            f"Generated {file_count} file(s) and deployed to sandbox. "
            f"Preview is live!"
        )
    elif sandbox_result.error:
        message = (
            f"Generated {file_count} file(s), but sandbox execution failed: "
            f"{sandbox_result.error}"
        )
    else:
        message = f"Generated {file_count} file(s). No preview available for this file type."

    return GenerateResponse(
        message=message,
        files=files,
        preview_url=sandbox_result.preview_url,
    )
