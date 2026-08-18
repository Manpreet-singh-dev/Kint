"""Tests for sandbox endpoint."""

from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.api.deps import get_sandbox_service


def test_sandbox_endpoint_success(client: TestClient, mock_sandbox_service: MagicMock):
    """Test GET /sandbox/test with mocked sandbox service."""
    app.dependency_overrides[get_sandbox_service] = lambda: mock_sandbox_service

    try:
        response = client.get("/sandbox/test")
        assert response.status_code == 200
        data = response.json()
        assert "preview_url" in data
        assert data["preview_url"] == "https://3000-test-sandbox.e2b.dev"
        assert data["error"] is None
        mock_sandbox_service.execute_files.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_versioned_sandbox_endpoint(client: TestClient, mock_sandbox_service: MagicMock):
    """Test GET /api/v1/sandbox/test works via versioned routing."""
    app.dependency_overrides[get_sandbox_service] = lambda: mock_sandbox_service

    try:
        response = client.get("/api/v1/sandbox/test")
        assert response.status_code == 200
        data = response.json()
        assert data["preview_url"] == "https://3000-test-sandbox.e2b.dev"
    finally:
        app.dependency_overrides.clear()
