"""
Pytest configuration and fixtures.

Follows the testing structure described in the Auth0 FastAPI best practices guide.
"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from app.main import app
from app.api.deps import get_coder_service, get_sandbox_service
from app.services.coder import CoderService
from app.services.sandbox import SandboxService
from app.schemas.sandbox import SandboxResult


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Test client fixture for FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_coder_service() -> MagicMock:
    """Mock CoderService fixture."""
    mock = MagicMock(spec=CoderService)
    mock.generate_files.return_value = {
        "index.html": "<!DOCTYPE html><html><body><h1>Mock App</h1></body></html>",
        "style.css": "body { background: #fff; }",
        "script.js": "console.log('Mock script');",
    }
    return mock


@pytest.fixture
def mock_sandbox_service() -> MagicMock:
    """Mock SandboxService fixture."""
    mock = MagicMock(spec=SandboxService)
    mock.execute_files = AsyncMock(
        return_value=SandboxResult(
            stdout="Serving HTTP on 0.0.0.0 port 8000 ...",
            stderr="",
            preview_url="https://8000-test-sandbox.e2b.dev",
            error=None,
        )
    )
    return mock
