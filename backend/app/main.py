"""
FastAPI application entry point.

Provides the /generate endpoint for accepting user prompts and orchestrating
the agent pipeline (Planner → Coder → Sandbox → Debugger).
"""

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .coder import generate_files_from_prompt, CodeGenerationError
from .sandbox import execute_files

# Load environment variables from .env file
load_dotenv()


app = FastAPI(title="AI App Builder", version="0.1.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """Request model for /generate endpoint."""
    prompt: str


class GenerateResponse(BaseModel):
    """Response model for /generate endpoint."""
    message: str
    files: dict[str, str]
    preview_url: str | None = None


class SandboxResponse(BaseModel):
    """Response model for /sandbox/test endpoint."""
    stdout: str
    stderr: str
    preview_url: str | None
    error: str | None


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI App Builder"}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    """
    Generate an app from a text prompt using Claude.

    Phase 1: Single-agent implementation - Coder agent generates files directly.
    Phase 2 will add: Planner → Coder → Sandbox → Debugger pipeline with retry logic.

    Args:
        request: Contains the user's text prompt

    Returns:
        GenerateResponse with message, generated files, and preview_url (None for now)

    Raises:
        HTTPException: If code generation fails (400 for user errors, 500 for system errors)
    """
    try:
        # Call Coder agent to generate files
        files = generate_files_from_prompt(request.prompt)

        return GenerateResponse(
            message=f"Generated {len(files)} file(s) based on your prompt. Preview coming in next task!",
            files=files,
            preview_url=None,  # Task 7 will connect sandbox execution
        )

    except CodeGenerationError as e:
        # User-facing errors (missing API key, bad response format)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Unexpected system errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during code generation: {str(e)}"
        )


@app.get("/sandbox/test", response_model=SandboxResponse)
async def test_sandbox():
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

    result = await execute_files(test_files)

    return SandboxResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        preview_url=result.preview_url,
        error=result.error,
    )
