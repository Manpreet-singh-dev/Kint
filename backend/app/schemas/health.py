from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(
        default="ok",
        description="Health status indicator",
        examples=["ok"],
    )
    service: str = Field(
        default="AI App Builder",
        description="Service name",
        examples=["AI App Builder"],
    )
    version: str = Field(
        default="0.1.0",
        description="API version",
        examples=["0.1.0"],
    )
