"""
FastAPI application entry point.

Provides the /generate endpoint for accepting user prompts and orchestrating
the agent pipeline (Planner → Coder → Sandbox → Debugger).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI App Builder"}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    """
    Generate an app from a text prompt.

    Currently returns a stub response. In future phases, this will:
    1. Send prompt to Planner agent for build steps
    2. Execute Coder agent for each step
    3. Run generated files in sandbox
    4. Trigger Debugger agent if execution fails

    Args:
        request: Contains the user's text prompt

    Returns:
        GenerateResponse with a message and generated files dict
    """
    # Stub response - no LLM call yet
    return GenerateResponse(
        message=f"Received prompt: '{request.prompt}'. App generation will be implemented in Phase 2.",
        files={
            "index.html": "<!DOCTYPE html><html><body><h1>Hello World</h1></body></html>",
            "style.css": "body { font-family: sans-serif; margin: 40px; }",
        }
    )
