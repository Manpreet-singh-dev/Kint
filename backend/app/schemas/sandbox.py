from typing import Optional
from pydantic import BaseModel, Field


class SandboxResult(BaseModel):
    """Internal result container for sandbox executions."""

    stdout: str = ""
    stderr: str = ""
    preview_url: Optional[str] = None
    error: Optional[str] = None


class SandboxResponse(BaseModel):
    """Response schema for sandbox test execution endpoint."""

    stdout: str = Field(
        default="",
        description="Standard output produced during sandbox execution",
        examples=["Serving HTTP on 0.0.0.0 port 8000 ..."],
    )
    stderr: str = Field(
        default="",
        description="Standard error output produced during sandbox execution",
        examples=[""],
    )
    preview_url: Optional[str] = Field(
        default=None,
        description="Preview URL if a web server was started in the sandbox",
        examples=["https://8000-sandbox-id.e2b.dev"],
    )
    error: Optional[str] = Field(
        default=None,
        description="Error description if execution encountered a failure",
        examples=[None],
    )
