"""Tests for code generation endpoint (full pipeline: generate → sandbox → preview)."""

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from app.main import app
from app.api.deps import get_coder_service, get_sandbox_service
from app.core.exceptions import CodeGenerationError, ConfigurationError
from app.schemas.sandbox import SandboxResult


def _override_deps(mock_coder, mock_sandbox):
    """Helper to set dependency overrides for both services."""
    app.dependency_overrides[get_coder_service] = lambda: mock_coder
    app.dependency_overrides[get_sandbox_service] = lambda: mock_sandbox


def test_generate_full_pipeline_success(
    client: TestClient,
    mock_coder_service: MagicMock,
    mock_sandbox_service: MagicMock,
):
    """Test full pipeline: prompt → Claude → sandbox → preview_url returned."""
    _override_deps(mock_coder_service, mock_sandbox_service)

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

        mock_coder_service.generate_files.assert_called_once_with("Create a modern timer app")
        mock_sandbox_service.execute_files.assert_called_once_with(
            mock_coder_service.generate_files.return_value
        )
    finally:
        app.dependency_overrides.clear()


def test_generate_sandbox_error_still_returns_files(
    client: TestClient,
    mock_coder_service: MagicMock,
):
    """Test that sandbox failure still returns generated files with error in message."""
    mock_sandbox = MagicMock()
    mock_sandbox.execute_files = AsyncMock(
        return_value=SandboxResult(
            stdout="",
            stderr="",
            preview_url=None,
            sandbox_id=None,
            error="E2B_API_KEY environment variable not set.",
        )
    )
    _override_deps(mock_coder_service, mock_sandbox)

    try:
        response = client.post("/generate", json={"prompt": "build a counter"})

        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert data["preview_url"] is None
        assert "sandbox execution failed" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_generate_endpoint_validation_error(
    client: TestClient,
    mock_coder_service: MagicMock,
    mock_sandbox_service: MagicMock,
):
    """Test POST /generate with empty prompt returns 422 Unprocessable Entity."""
    _override_deps(mock_coder_service, mock_sandbox_service)

    try:
        response = client.post("/generate", json={"prompt": ""})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_generate_code_generation_error_handled(
    client: TestClient,
    mock_coder_service: MagicMock,
    mock_sandbox_service: MagicMock,
):
    """Test that CodeGenerationError is handled by custom exception handler returning 400."""
    mock_coder_service.generate_files.side_effect = CodeGenerationError(
        "No files were generated. The model may not have followed the expected format."
    )
    _override_deps(mock_coder_service, mock_sandbox_service)

    try:
        response = client.post("/generate", json={"prompt": "invalid prompt"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "CodeGenerationError"
        assert "No files were generated" in data["message"]
        # Sandbox should NOT be called if code generation fails
        mock_sandbox_service.execute_files.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_generate_configuration_error_handled(
    client: TestClient,
    mock_coder_service: MagicMock,
    mock_sandbox_service: MagicMock,
):
    """Test that ConfigurationError is handled by custom exception handler returning 400/500."""
    mock_coder_service.generate_files.side_effect = ConfigurationError(
        "ANTHROPIC_API_KEY environment variable not set.",
        status_code=400,
    )
    _override_deps(mock_coder_service, mock_sandbox_service)

    try:
        response = client.post("/generate", json={"prompt": "build an app"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "ConfigurationError"
        assert "ANTHROPIC_API_KEY" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_versioned_generate_endpoint(
    client: TestClient,
    mock_coder_service: MagicMock,
    mock_sandbox_service: MagicMock,
):
    """Test POST /api/v1/generate works via versioned routing."""
    _override_deps(mock_coder_service, mock_sandbox_service)

    try:
        response = client.post("/api/v1/generate", json={"prompt": "Build a calculator"})
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert data["preview_url"] == "https://3000-test-sandbox.e2b.dev"
    finally:
        app.dependency_overrides.clear()
