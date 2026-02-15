"""FastAPI application for the Spec-to-Test Generator API."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.generator import generate_test_code
from app.models import HealthResponse

app = FastAPI(
    title="Spec-to-Test Generator API",
    description=(
        "A REST API that accepts an OpenAPI 3.x specification and "
        "generates a runnable pytest test suite covering happy paths, "
        "error cases, and schema validation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.post(
    "/generate",
    response_class=PlainTextResponse,
    tags=["Generator"],
    summary="Generate pytest tests from an OpenAPI spec",
    description=(
        "Accepts an OpenAPI 3.x JSON spec in the request body and returns "
        "generated pytest code as plain text."
    ),
    responses={
        200: {"description": "Generated pytest code", "content": {"text/plain": {}}},
        400: {"description": "Invalid OpenAPI spec"},
        422: {"description": "Request body missing or not valid JSON"},
    },
)
async def generate_tests(request: Request) -> PlainTextResponse:
    """Accept an OpenAPI spec and return generated pytest test code."""
    # Parse JSON body - FastAPI will return 422 automatically if body is missing
    # or not valid JSON, but we handle it explicitly for clarity.
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=422,
            content={"detail": "Request body must be valid JSON."},
        )

    # Validate that it looks like an OpenAPI spec
    if not isinstance(body, dict):
        return JSONResponse(
            status_code=400,
            content={"detail": "Request body must be a JSON object."},
        )

    missing_keys = []
    for key in ("openapi", "info", "paths"):
        if key not in body:
            missing_keys.append(key)

    if missing_keys:
        return JSONResponse(
            status_code=400,
            content={
                "detail": (
                    f"Invalid OpenAPI spec: missing required key(s): "
                    f"{', '.join(missing_keys)}. "
                    f"A valid OpenAPI spec must include 'openapi', 'info', and 'paths'."
                )
            },
        )

    # Validate OpenAPI version (must be 3.x)
    openapi_version = str(body.get("openapi", ""))
    if not openapi_version.startswith("3."):
        return JSONResponse(
            status_code=400,
            content={
                "detail": (
                    f"Unsupported OpenAPI version '{openapi_version}'. "
                    f"Only OpenAPI 3.x specs are supported."
                )
            },
        )

    # Validate that paths is a JSON object
    if not isinstance(body.get("paths"), dict):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "'paths' must be a JSON object mapping paths to path items."
            },
        )

    # Generate the test code
    code = generate_test_code(body)

    return PlainTextResponse(content=code, status_code=200)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Returns the health status of the API.",
)
async def health_check() -> HealthResponse:
    """Return a simple health check response."""
    return HealthResponse(status="ok")
