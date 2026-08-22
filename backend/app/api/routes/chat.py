"""
API Route for Grounded Codebase Q&A ('Chat about this app').

Role in Pipeline:
Provides a conversational endpoint where users can ask questions about a generated
application. Answers are strictly grounded in semantic code chunks retrieved from
PostgreSQL + pgvector via the ChatGroundingService.
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_chat_grounding_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_grounding import ChatGroundingService


router = APIRouter(tags=["Chat Grounding"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat about Generated Application",
    description=(
        "Ask questions, request architectural explanations, or discuss feature extensions "
        "for a specific generated application codebase, grounded in vector embeddings."
    ),
    responses={
        400: {"description": "Bad Request or Validation Error"},
        500: {"description": "Internal Server Error or LLM Provider Failure"},
    },
)
async def chat_about_app(
    request: ChatRequest,
    chat_service: ChatGroundingService = Depends(get_chat_grounding_service),
) -> ChatResponse:
    """
    Handle grounded conversational Q&A over an indexed application codebase.

    Pipeline:
    1. Query pgvector for semantic code chunks matching the question for app_id.
    2. Format code excerpts as grounding context.
    3. Invoke LLM provider with grounding system prompt.
    4. Return AI response and source code citations with similarity scores.
    """
    return chat_service.answer_question(
        app_id=request.app_id,
        message=request.message,
        history=request.history,
    )
