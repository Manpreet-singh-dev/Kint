"""Code generation API endpoints."""

from fastapi import APIRouter, Depends, status
from app.api.deps import get_orchestrator_service
from app.core.exceptions import CodeGenerationError
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.orchestrator import AgentState, OrchestratorService

router = APIRouter(tags=["Code Generation"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Application Files via Multi-Agent Orchestration",
    description=(
        "Generate a complete web application from a natural language prompt "
        "using a multi-agent orchestration loop (Planner → Coder → Sandbox → Debugger)."
    ),
    responses={
        400: {
            "description": "Bad Request or Code Generation Error",
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
                        "message": "GROK_API_KEY / GROQ_API_KEY environment variable not set.",
                        "detail": "GROK_API_KEY / GROQ_API_KEY environment variable not set.",
                    }
                }
            },
        },
    },
)
async def generate_application(
    request: GenerateRequest,
    orchestrator_service: OrchestratorService = Depends(get_orchestrator_service),
) -> GenerateResponse:
    """
    Generate an app from a text prompt using the Multi-Agent Orchestrator loop.

    Pipeline: User Prompt → Planner Agent → Coder Agent → E2B Sandbox → (Debugger retry loop) → Live Preview.
    """
    context = await orchestrator_service.run_pipeline(
        prompt=request.prompt,
        prior_files=request.current_files,
    )

    if context.current_state == AgentState.FAILED and not context.files:
        raise CodeGenerationError(
            context.error_message or "Failed to generate application files after multiple attempts."
        )

    return GenerateResponse(
        message=context.message,
        files=context.files,
        preview_url=context.preview_url,
    )
