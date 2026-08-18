"""Tests for code generation endpoint."""

from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.api.deps import get_coder_service
from app.core.exceptions import CodeGenerationError, ConfigurationError


def test_generate_endpoint_success(client: TestClient, mock_coder_service: MagicMock):
    """Test successful POST /generate with mocked coder service."""
    app.dependency_overrides[get_coder_service] = lambda: mock_coder_service

    try:
        payload = {"prompt": "Create a modern timer app"}
        response = client.post("/generate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "files" in data
        assert "index.html" in data["files"]
        mock_coder_service.generate_files.assert_called_once_with("Create a modern timer app")
    finally:
        app.dependency_overrides.clear()


def test_generate_endpoint_validation_error(client: TestClient):
    """Test POST /generate with empty prompt returns 422 Unprocessable Entity."""
    response = client.post("/generate", json={"prompt": ""})
    assert response.status_code == 422


def test_generate_code_generation_error_handled(client: TestClient, mock_coder_service: MagicMock):
    """Test that CodeGenerationError is handled by custom exception handler returning 400."""
    mock_coder_service.generate_files.side_effect = CodeGenerationError(
        "No files were generated. The model may not have followed the expected format."
    )
    app.dependency_overrides[get_coder_service] = lambda: mock_coder_service

    try:
        response = client.post("/generate", json={"prompt": "invalid prompt"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "CodeGenerationError"
        assert "No files were generated" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_generate_configuration_error_handled(client: TestClient, mock_coder_service: MagicMock):
    """Test that ConfigurationError is handled by custom exception handler returning 400/500."""
    mock_coder_service.generate_files.side_effect = ConfigurationError(
        "ANTHROPIC_API_KEY environment variable not set.",
        status_code=400,
    )
    app.dependency_overrides[get_coder_service] = lambda: mock_coder_service

    try:
        response = client.post("/generate", json={"prompt": "build an app"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "ConfigurationError"
        assert "ANTHROPIC_API_KEY" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_versioned_generate_endpoint(client: TestClient, mock_coder_service: MagicMock):
    """Test POST /api/v1/generate works via versioned routing."""
    app.dependency_overrides[get_coder_service] = lambda: mock_coder_service

    try:
        response = client.post("/api/v1/generate", json={"prompt": "Build a calculator"})
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
    finally:
        app.dependency_overrides.clear()
