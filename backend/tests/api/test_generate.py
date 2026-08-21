"""Tests for code generation endpoint (full pipeline: generate → sandbox → preview)."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from app.main import app
from app.api.deps import get_orchestrator_service
from app.core.exceptions import CodeGenerationError, ConfigurationError
from app.services.orchestrator import AgentExecutionContext, AgentState


def _override_orchestrator(mock_orchestrator):
    """Helper to set dependency override for OrchestratorService."""
    app.dependency_overrides[get_orchestrator_service] = lambda: mock_orchestrator


def test_generate_full_pipeline_success(client: TestClient):
    """Test full pipeline: prompt → Orchestrator → preview_url returned."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_pipeline = AsyncMock(
        return_value=AgentExecutionContext(
            prompt="Create a modern timer app",
            current_state=AgentState.DONE,
            files={"index.html": "<!DOCTYPE html><html><body><h1>Timer</h1></body></html>"},
            preview_url="https://3000-test-sandbox.e2b.dev",
            message="Generated 1 file(s) and deployed to sandbox. Preview is live!",
        )
    )
    _override_orchestrator(mock_orchestrator)

    try:
        payload = {"prompt": "Create a modern timer app"}
        response = client.post("/generate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "files" in data
        assert "preview_url" in data
        assert "index.html" in data["files"]
        assert data["preview_url"] == "https://3000-test-sandbox.e2b.dev"
        assert "deployed to sandbox" in data["message"]

        mock_orchestrator.run_pipeline.assert_called_once_with("Create a modern timer app")
    finally:
        app.dependency_overrides.clear()


def test_generate_sandbox_error_still_returns_files(client: TestClient):
    """Test that sandbox failure still returns generated files with error in message."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_pipeline = AsyncMock(
        return_value=AgentExecutionContext(
            prompt="build a counter",
            current_state=AgentState.DONE,
            files={"index.html": "<!DOCTYPE html><html><body><h1>Counter</h1></body></html>"},
            preview_url=None,
            message="Generated 1 file(s), but sandbox execution failed: E2B_API_KEY environment variable not set.",
        )
    )
    _override_orchestrator(mock_orchestrator)

    try:
        response = client.post("/generate", json={"prompt": "build a counter"})

        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert data["preview_url"] is None
        assert "sandbox execution failed" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_generate_endpoint_validation_error(client: TestClient):
    """Test POST /generate with empty prompt returns 422 Unprocessable Entity."""
    mock_orchestrator = MagicMock()
    _override_orchestrator(mock_orchestrator)

    try:
        response = client.post("/generate", json={"prompt": ""})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_generate_code_generation_error_handled(client: TestClient):
    """Test that CodeGenerationError is handled by custom exception handler returning 400."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_pipeline = AsyncMock(
        side_effect=CodeGenerationError(
            "No files were generated. The model may not have followed the expected format."
        )
    )
    _override_orchestrator(mock_orchestrator)

    try:
        response = client.post("/generate", json={"prompt": "invalid prompt"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "CodeGenerationError"
        assert "No files were generated" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_generate_configuration_error_handled(client: TestClient):
    """Test that ConfigurationError is handled by custom exception handler returning 400/500."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_pipeline = AsyncMock(
        side_effect=ConfigurationError(
            "GROK_API_KEY environment variable not set.",
            status_code=400,
        )
    )
    _override_orchestrator(mock_orchestrator)

    try:
        response = client.post("/generate", json={"prompt": "build an app"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "ConfigurationError"
        assert "GROK_API_KEY" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_versioned_generate_endpoint(client: TestClient):
    """Test POST /api/v1/generate works via versioned routing."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_pipeline = AsyncMock(
        return_value=AgentExecutionContext(
            prompt="Build a calculator",
            current_state=AgentState.DONE,
            files={"index.html": "<!DOCTYPE html><html><body><h1>Calc</h1></body></html>"},
            preview_url="https://3000-test-sandbox.e2b.dev",
            message="Generated 1 file(s). Preview is live!",
        )
    )
    _override_orchestrator(mock_orchestrator)

    try:
        response = client.post("/api/v1/generate", json={"prompt": "Build a calculator"})
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert data["preview_url"] == "https://3000-test-sandbox.e2b.dev"
    finally:
        app.dependency_overrides.clear()
