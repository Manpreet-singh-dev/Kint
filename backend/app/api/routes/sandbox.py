"""Sandbox API endpoints."""

from fastapi import APIRouter, Depends, status
from app.api.deps import get_sandbox_service
from app.schemas.sandbox import SandboxResponse
from app.services.sandbox import SandboxService

router = APIRouter(prefix="/sandbox", tags=["Sandbox"])


@router.get(
    "/test",
    response_model=SandboxResponse,
    status_code=status.HTTP_200_OK,
    summary="Test Sandbox Execution",
    description="Verify E2B sandbox integration by running a test HTML web application.",
)
async def test_sandbox(
    sandbox_service: SandboxService = Depends(get_sandbox_service),
) -> SandboxResponse:
    """
    Test endpoint to verify E2B sandbox integration.

    Creates a simple HTML file and executes it in the sandbox.
    Returns execution results and preview URL.
    """
    test_files = {
        "index.html": """<!DOCTYPE html>
<html>
<head>
    <title>E2B Test</title>
    <style>
        body {
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 0.5em;
        }
        p {
            font-size: 1.5em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ E2B Sandbox Working!</h1>
        <p>This page is running in an isolated E2B sandbox</p>
    </div>
</body>
</html>"""
    }

    result = await sandbox_service.execute_files(test_files)

    return SandboxResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        preview_url=result.preview_url,
        error=result.error,
    )
