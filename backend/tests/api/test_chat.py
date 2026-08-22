"""Tests for Chat Grounding Endpoint and Service (Phase 3 RAG & Codebase Q&A)."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.api.deps import get_chat_grounding_service
from app.main import app
from app.schemas.chat import ChatMessage, ChatResponse, CodeSourceCitation
from app.services.chat_grounding import ChatGroundingService
from app.services.vector_store import VectorSearchResult


def test_chat_grounding_service_answer_question():
    """Test ChatGroundingService retrieves relevant snippets and generates grounded answer."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = (
        "The timer is implemented in `script.js` using `setInterval` inside the `startTimer` function."
    )

    mock_indexer = MagicMock()
    mock_indexer.query_app_code.return_value = [
        VectorSearchResult(
            chunk_id=1,
            collection_name="app_code",
            document_id="app_123:script.js:0",
            content="function startTimer() { interval = setInterval(tick, 1000); }",
            metadata={"file_name": "script.js", "section_name": "startTimer", "app_id": "app_123"},
            similarity_score=0.95,
        )
    ]

    service = ChatGroundingService(provider=mock_provider, app_indexer=mock_indexer)
    history = [ChatMessage(role="user", content="Hi"), ChatMessage(role="assistant", content="Hello!")]

    chat_resp = service.answer_question(
        app_id="app_123",
        message="How does the timer start?",
        history=history,
    )

    assert isinstance(chat_resp, ChatResponse)
    assert chat_resp.app_id == "app_123"
    assert "startTimer" in chat_resp.response
    assert len(chat_resp.sources) == 1
    assert chat_resp.sources[0].file_name == "script.js"
    assert chat_resp.sources[0].section_name == "startTimer"

    mock_indexer.query_app_code.assert_called_once_with(app_id="app_123", query="How does the timer start?", limit=4)
    call_args = mock_provider.generate_text.call_args
    assert "startTimer" in call_args.kwargs["user_prompt"]
    assert "Conversation History" in call_args.kwargs["user_prompt"]


def test_chat_endpoint_success(client: TestClient):
    """Test POST /chat returns 200 with grounded response and source citations."""
    mock_chat_service = MagicMock()
    mock_chat_service.answer_question.return_value = ChatResponse(
        app_id="app_test",
        response="The canvas renders via `requestAnimationFrame`.",
        sources=[
            CodeSourceCitation(
                file_name="script.js",
                section_name="renderLoop",
                content="function renderLoop() { ... }",
                similarity_score=0.92,
            )
        ],
    )

    app.dependency_overrides[get_chat_grounding_service] = lambda: mock_chat_service

    try:
        payload = {
            "app_id": "app_test",
            "message": "How is animation handled?",
            "history": [],
        }
        response = client.post("/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["app_id"] == "app_test"
        assert "requestAnimationFrame" in data["response"]
        assert len(data["sources"]) == 1
        assert data["sources"][0]["file_name"] == "script.js"

        mock_chat_service.answer_question.assert_called_once_with(
            app_id="app_test",
            message="How is animation handled?",
            history=[],
        )
    finally:
        app.dependency_overrides.clear()


def test_chat_endpoint_validation_error(client: TestClient):
    """Test POST /chat with empty message returns 422 Unprocessable Entity."""
    response = client.post("/chat", json={"app_id": "app_test", "message": ""})
    assert response.status_code == 422
