"""Pydantic models for the Test Case Manager API."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priority levels for test cases."""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, Enum):
    """Status options for test cases."""
    active = "active"
    inactive = "inactive"
    draft = "draft"


class TestCaseCreate(BaseModel):
    """Schema for creating a new test case."""
    title: str = Field(..., min_length=1, description="Title of the test case")
    description: str = Field(..., description="Detailed description of the test case")
    steps: str = Field(..., description="Steps to reproduce or execute the test")
    expected_result: str = Field(..., description="Expected outcome of the test")
    priority: Priority = Field(..., description="Priority level")
    status: Status = Field(..., description="Current status")
    tags: list[str] = Field(default=[], description="Tags for categorization")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Login with valid credentials",
                    "description": "Verify that a user can log in with correct username and password",
                    "steps": "1. Navigate to /login\n2. Enter valid username\n3. Enter valid password\n4. Click Submit",
                    "expected_result": "User is redirected to the dashboard",
                    "priority": "high",
                    "status": "active",
                    "tags": ["smoke", "regression", "auth"],
                }
            ]
        }
    }


class TestCaseUpdate(BaseModel):
    """Schema for updating an existing test case. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, description="Title of the test case")
    description: Optional[str] = Field(None, description="Detailed description of the test case")
    steps: Optional[str] = Field(None, description="Steps to reproduce or execute the test")
    expected_result: Optional[str] = Field(None, description="Expected outcome of the test")
    priority: Optional[Priority] = Field(None, description="Priority level")
    status: Optional[Status] = Field(None, description="Current status")
    tags: Optional[list[str]] = Field(None, description="Tags for categorization")


class TestCaseResponse(BaseModel):
    """Schema for a test case response."""
    id: int = Field(..., description="Unique identifier")
    title: str = Field(..., description="Title of the test case")
    description: str = Field(..., description="Detailed description of the test case")
    steps: str = Field(..., description="Steps to reproduce or execute the test")
    expected_result: str = Field(..., description="Expected outcome of the test")
    priority: Priority = Field(..., description="Priority level")
    status: Status = Field(..., description="Current status")
    tags: list[str] = Field(..., description="Tags for categorization")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Login with valid credentials",
                    "description": "Verify that a user can log in with correct username and password",
                    "steps": "1. Navigate to /login\n2. Enter valid username\n3. Enter valid password\n4. Click Submit",
                    "expected_result": "User is redirected to the dashboard",
                    "priority": "high",
                    "status": "active",
                    "tags": ["smoke", "regression", "auth"],
                    "created_at": "2026-02-14T12:00:00+00:00",
                    "updated_at": "2026-02-14T12:00:00+00:00",
                }
            ]
        }
    }
