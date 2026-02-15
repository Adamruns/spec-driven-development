"""Core logic for parsing OpenAPI specs and generating pytest test code."""

from __future__ import annotations

import re
from typing import Any


def _sanitize_path_for_name(path: str) -> str:
    """Convert an OpenAPI path like /pets/{petId} to a snake_case name like pets_pet_id.

    Rules:
    - Strip leading/trailing slashes
    - Replace path parameter braces: {petId} -> pet_id (camelCase to snake_case)
    - Replace remaining slashes and hyphens with underscores
    - Collapse multiple underscores
    """
    # Remove leading/trailing slashes
    clean = path.strip("/")

    # Convert {paramName} -> param_name (handle camelCase inside braces)
    def _brace_to_snake(match: re.Match) -> str:
        name = match.group(1)
        # camelCase to snake_case
        snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
        return snake

    clean = re.sub(r"\{([^}]+)\}", _brace_to_snake, clean)

    # Replace slashes, hyphens, dots with underscores
    clean = re.sub(r"[/\-.]", "_", clean)

    # Collapse multiple underscores and strip trailing
    clean = re.sub(r"_+", "_", clean).strip("_")

    return clean


def _has_path_params(path: str) -> bool:
    """Check if a path contains any path parameters like {id}."""
    return bool(re.search(r"\{[^}]+\}", path))


def _get_lowest_2xx_status(responses: dict[str, Any]) -> int:
    """Find the lowest 2xx status code from a responses dict.

    Falls back to 200 if no 2xx codes are found.
    """
    status_codes = []
    for key in responses:
        try:
            code = int(key)
            if 200 <= code < 300:
                status_codes.append(code)
        except (ValueError, TypeError):
            continue

    return min(status_codes) if status_codes else 200


def _get_response_schema(responses: dict[str, Any], status_code: int) -> dict | None:
    """Extract the JSON response schema for a given status code, if defined.

    Returns None if the schema contains $ref (unresolved references cannot
    be used with jsonschema.validate without a resolver).
    """
    resp = responses.get(str(status_code), {})
    content = resp.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema")
    if schema and _contains_ref(schema):
        return None
    return schema


def _contains_ref(obj: Any) -> bool:
    """Check if a schema dict contains any $ref keys (unresolved references)."""
    if isinstance(obj, dict):
        if "$ref" in obj:
            return True
        return any(_contains_ref(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_ref(item) for item in obj)
    return False


def _has_required_request_body(operation: dict[str, Any]) -> bool:
    """Check if an operation has a required request body.

    Per the OpenAPI 3.x spec, ``requestBody.required`` defaults to ``False``.
    We only generate missing-body tests when the body is explicitly required.
    """
    request_body = operation.get("requestBody", {})
    if not request_body:
        return False
    if not request_body.get("content"):
        return False
    return bool(request_body.get("required", False))


def _get_request_body_schema(operation: dict[str, Any]) -> dict | None:
    """Extract the JSON request body schema if defined."""
    request_body = operation.get("requestBody", {})
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    return json_content.get("schema")


def _generate_sample_value(schema: dict[str, Any] | None) -> Any:
    """Generate a minimal sample value from a JSON schema.

    This produces valid-looking sample data for request bodies.
    """
    if schema is None:
        return {}

    schema_type = schema.get("type", "object")

    if schema_type == "string":
        enum = schema.get("enum")
        if enum:
            return enum[0]
        fmt = schema.get("format", "")
        if fmt == "email":
            return "user@example.com"
        if fmt == "date":
            return "2026-01-01"
        if fmt == "date-time":
            return "2026-01-01T00:00:00Z"
        if fmt == "uri" or fmt == "url":
            return "https://example.com"
        return "string"
    elif schema_type == "integer":
        return 1
    elif schema_type == "number":
        return 1.0
    elif schema_type == "boolean":
        return True
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        return [_generate_sample_value(items_schema)]
    elif schema_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        result = {}
        # Include required properties first, then all properties
        for prop_name, prop_schema in properties.items():
            result[prop_name] = _generate_sample_value(prop_schema)
        # If no properties defined, return empty dict
        return result
    else:
        return "string"


def _make_path_with_sample_values(path: str) -> str:
    """Replace path parameters with sample values for test code.

    E.g., /pets/{petId} -> /pets/1
    """
    return re.sub(r"\{[^}]+\}", "1", path)


def _make_path_with_nonexistent_values(path: str) -> str:
    """Replace path parameters with non-existent values for 404 tests.

    E.g., /pets/{petId} -> /pets/999999
    """
    return re.sub(r"\{[^}]+\}", "999999", path)


def _unique_name(base: str, used: set[str]) -> str:
    """Return a unique function name, appending a counter if needed."""
    name = base
    counter = 2
    while name in used:
        name = f"{base}_{counter}"
        counter += 1
    used.add(name)
    return name


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def parse_openapi_spec(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse an OpenAPI spec into a list of endpoint descriptors.

    Each descriptor contains:
    - path: the URL path
    - method: HTTP method (lowercase)
    - operation: the full operation object
    - has_path_params: whether the path has parameters
    - has_request_body: whether a request body is defined
    - status_code: lowest 2xx status code
    - response_schema: JSON schema of the response (or None)
    - request_body_schema: JSON schema of the request body (or None)
    - sanitized_name: snake_case name for test functions

    Returns endpoints sorted by (path, method) for deterministic output.
    """
    paths = spec.get("paths", {})
    endpoints = []

    for path in sorted(paths.keys()):
        path_item = paths[path]
        if not isinstance(path_item, dict):
            continue

        for method in sorted(path_item.keys()):
            if method.lower() not in HTTP_METHODS:
                continue

            operation = path_item[method]
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses", {})
            status_code = _get_lowest_2xx_status(responses)
            response_schema = _get_response_schema(responses, status_code)

            endpoints.append({
                "path": path,
                "method": method.lower(),
                "operation": operation,
                "has_path_params": _has_path_params(path),
                "has_request_body": _has_required_request_body(operation),
                "status_code": status_code,
                "response_schema": response_schema,
                "request_body_schema": _get_request_body_schema(operation),
                "sanitized_name": _sanitize_path_for_name(path),
            })

    return endpoints


def generate_test_code(spec: dict[str, Any]) -> str:
    """Generate a complete, runnable pytest test file from an OpenAPI spec.

    The generated code includes:
    - Imports for pytest, requests, and jsonschema
    - A configurable BASE_URL
    - Happy-path tests for each endpoint
    - 404 tests for endpoints with path parameters
    - 422/400 tests for endpoints with required request bodies
    - Response schema validation where schemas are defined
    """
    endpoints = parse_openapi_spec(spec)

    lines: list[str] = []

    # --- Imports ---
    lines.append("import requests")
    lines.append("from jsonschema import validate")
    lines.append("")
    lines.append("")
    lines.append('BASE_URL = "http://localhost:8000"')
    lines.append("")

    if not endpoints:
        # Produce a minimal valid file even if no endpoints
        lines.append("")
        lines.append("# No endpoints found in the provided OpenAPI spec.")
        lines.append("")
        return "\n".join(lines)

    used_names: set[str] = set()

    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        sanitized = ep["sanitized_name"]
        status_code = ep["status_code"]
        response_schema = ep["response_schema"]
        has_path_params = ep["has_path_params"]
        has_request_body = ep["has_request_body"]
        request_body_schema = ep["request_body_schema"]

        func_base = _unique_name(f"{method}_{sanitized}", used_names)
        sample_path = _make_path_with_sample_values(path)

        # --- Happy-path test ---
        lines.append("")
        lines.append(f"def test_{func_base}_success():")

        # Build the request call
        if has_request_body:
            sample_body = _generate_sample_value(request_body_schema)
            lines.append(f"    payload = {repr(sample_body)}")
            lines.append(
                f'    response = requests.{method}(f"{{BASE_URL}}{sample_path}", json=payload)'
            )
        else:
            lines.append(
                f'    response = requests.{method}(f"{{BASE_URL}}{sample_path}")'
            )

        lines.append(f"    assert response.status_code == {status_code}")

        # Schema validation
        if response_schema is not None:
            lines.append(f"    schema = {repr(response_schema)}")
            lines.append("    validate(instance=response.json(), schema=schema)")

        lines.append("")

        # --- 404 test for path params ---
        if has_path_params:
            not_found_path = _make_path_with_nonexistent_values(path)
            lines.append("")
            lines.append(f"def test_{func_base}_not_found():")
            if has_request_body:
                sample_body = _generate_sample_value(request_body_schema)
                lines.append(f"    payload = {repr(sample_body)}")
                lines.append(
                    f'    response = requests.{method}(f"{{BASE_URL}}{not_found_path}", json=payload)'
                )
            else:
                lines.append(
                    f'    response = requests.{method}(f"{{BASE_URL}}{not_found_path}")'
                )
            lines.append("    assert response.status_code == 404")
            lines.append("")

        # --- Missing body test ---
        if has_request_body:
            lines.append("")
            lines.append(f"def test_{func_base}_missing_body():")
            lines.append(
                f'    response = requests.{method}(f"{{BASE_URL}}{sample_path}", json={{}})'
            )
            lines.append("    assert response.status_code in [400, 422]")
            lines.append("")

    # Ensure file ends with a single newline
    result = "\n".join(lines)
    # Clean up excessive blank lines (max 2 consecutive)
    result = re.sub(r"\n{4,}", "\n\n\n", result)
    if not result.endswith("\n"):
        result += "\n"

    return result
