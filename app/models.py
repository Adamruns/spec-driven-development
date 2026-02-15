"""Pydantic models for the Spec-to-Test Generator API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""

    status: str = Field(..., description="Health status")
