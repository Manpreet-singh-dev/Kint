"""Pydantic schemas for the 'Chat about this app' Q&A grounding endpoint."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat history turn."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    """Request payload for chatting about an indexed application."""
    app_id: str = Field(..., min_length=1, description="Target application identifier")
    message: str = Field(..., min_length=1, description="User question or inquiry about the codebase")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Prior conversation history")


class CodeSourceCitation(BaseModel):
    """Referenced codebase snippet grounded in pgvector embeddings."""
    file_name: str
    section_name: Optional[str] = None
    content: str
    similarity_score: float


class ChatResponse(BaseModel):
    """Response returned from grounded chat endpoint."""
    app_id: str
    response: str
    sources: List[CodeSourceCitation] = Field(default_factory=list)
