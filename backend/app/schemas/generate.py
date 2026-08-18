from typing import Dict, Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request schema for code generation endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        description="Natural language description of the web application to generate",
        examples=["Build a modern stopwatch app with lap times and dark mode"],
    )


class GenerateResponse(BaseModel):
    """Response schema for code generation endpoint."""

    message: str = Field(
        ...,
        description="Human-readable status or summary of generation",
        examples=["Generated 3 file(s) based on your prompt."],
    )
    files: Dict[str, str] = Field(
        ...,
        description="Dictionary mapping generated filenames to their source code",
        examples=[
            {
                "index.html": "<!DOCTYPE html>\n<html>\n<head><title>Stopwatch</title></head>\n<body>...</body>\n</html>",
                "style.css": "body { font-family: sans-serif; }",
                "script.js": "// stopwatch logic",
            }
        ],
    )
    preview_url: Optional[str] = Field(
        default=None,
        description="Live preview URL of the running application in the sandbox",
        examples=["https://8000-sandbox-id.e2b.dev"],
    )
