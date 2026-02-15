"""FastAPI application for the Test Case Manager API."""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from app.db import (
    create_test_case,
    delete_test_case,
    get_test_case_by_id,
    get_test_cases,
    init_db,
    update_test_case,
)
from app.models import (
    Priority,
    Status,
    TestCaseCreate,
    TestCaseResponse,
    TestCaseUpdate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on application startup."""
    init_db()
    yield


app = FastAPI(
    title="Test Case Manager API",
    description=(
        "A RESTful API for managing test cases. "
        "Supports full CRUD operations with filtering by status, priority, and tag. "
        "Built with FastAPI, SQLite, and Pydantic."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.post(
    "/test-cases",
    response_model=TestCaseResponse,
    status_code=201,
    tags=["Test Cases"],
    summary="Create a new test case",
    description="Create a new test case with the provided details. All required fields must be supplied.",
)
def create_test_case_endpoint(test_case: TestCaseCreate) -> TestCaseResponse:
    """Create a new test case and return the created resource."""
    result = create_test_case(test_case.model_dump())
    return TestCaseResponse(**result)


@app.get(
    "/test-cases",
    response_model=list[TestCaseResponse],
    status_code=200,
    tags=["Test Cases"],
    summary="List all test cases",
    description="Retrieve all test cases, with optional filtering by status, priority, and/or tag.",
)
def list_test_cases_endpoint(
    status: Optional[Status] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
) -> list[TestCaseResponse]:
    """List all test cases with optional filters."""
    status_val = status.value if status else None
    priority_val = priority.value if priority else None
    results = get_test_cases(status=status_val, priority=priority_val, tag=tag)
    return [TestCaseResponse(**r) for r in results]


@app.get(
    "/test-cases/{test_case_id}",
    response_model=TestCaseResponse,
    status_code=200,
    tags=["Test Cases"],
    summary="Get a test case by ID",
    description="Retrieve a single test case by its unique identifier.",
    responses={404: {"description": "Test case not found"}},
)
def get_test_case_endpoint(test_case_id: int) -> TestCaseResponse:
    """Get a single test case by ID."""
    result = get_test_case_by_id(test_case_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return TestCaseResponse(**result)


@app.put(
    "/test-cases/{test_case_id}",
    response_model=TestCaseResponse,
    status_code=200,
    tags=["Test Cases"],
    summary="Update a test case",
    description="Update an existing test case. Only the fields provided will be updated.",
    responses={404: {"description": "Test case not found"}},
)
def update_test_case_endpoint(
    test_case_id: int, test_case: TestCaseUpdate
) -> TestCaseResponse:
    """Update a test case by ID."""
    update_data = test_case.model_dump(exclude_unset=True)
    result = update_test_case(test_case_id, update_data)
    if result is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return TestCaseResponse(**result)


@app.delete(
    "/test-cases/{test_case_id}",
    status_code=200,
    tags=["Test Cases"],
    summary="Delete a test case",
    description="Delete a test case by its unique identifier.",
    responses={404: {"description": "Test case not found"}},
)
def delete_test_case_endpoint(test_case_id: int) -> dict:
    """Delete a test case by ID."""
    deleted = delete_test_case(test_case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test case not found")
    return {"detail": "Test case deleted", "id": test_case_id}
