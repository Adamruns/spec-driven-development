"""API tests for the Spec-to-Test Generator.

Tests are mapped to Acceptance Criteria defined in SPECS/spec-to-test-generator.md.

AC1:  POST /generate with a valid OpenAPI spec returns 200 with generated pytest code
AC2:  Generated tests include a happy-path test for each endpoint+method in the spec
AC3:  Generated tests include jsonschema validation for endpoints with defined response schemas
AC4:  Generated tests include 404 tests for endpoints with path parameters
AC5:  Generated tests include 422 tests for endpoints with required request body fields
AC6:  POST /generate with invalid/non-OpenAPI JSON returns 400 with a descriptive error message
AC7:  POST /generate with missing or empty body returns 422
AC8:  GET /health returns 200 with status "ok"
AC9:  Generated test code is syntactically valid Python (compiles without errors)
AC10: Swagger UI is accessible at /docs
"""

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _generate(client, spec: dict) -> "httpx.Response":
    """POST a spec to /generate and return the response."""
    return client.post("/generate", json=spec)


# ---------------------------------------------------------------------------
# AC1 & AC9: POST /generate with valid spec returns 200 with pytest code
# ---------------------------------------------------------------------------

class TestGenerate:
    """Tests for successful POST /generate calls."""

    def test_generate_returns_200(self, client, sample_openapi_spec):
        """AC1: POST /generate with a valid OpenAPI spec returns HTTP 200."""
        response = _generate(client, sample_openapi_spec)
        assert response.status_code == 200

    def test_generate_returns_text_content_type(self, client, sample_openapi_spec):
        """AC1: The response Content-Type is text/plain (generated Python code)."""
        response = _generate(client, sample_openapi_spec)
        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type

    def test_generate_response_is_non_empty(self, client, sample_openapi_spec):
        """AC1: The generated output is not empty."""
        response = _generate(client, sample_openapi_spec)
        assert len(response.text.strip()) > 0

    # -------------------------------------------------------------------
    # AC2: Happy-path tests for each endpoint+method
    # -------------------------------------------------------------------

    def test_generated_code_has_get_pets_test(self, client, sample_openapi_spec):
        """AC2: Generated code includes a happy-path test for GET /pets."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # Should contain a test function that exercises GET /pets
        assert "def test_" in code
        assert "/pets" in code
        # At least one GET call for /pets
        assert "get" in code.lower()

    def test_generated_code_has_post_pets_test(self, client, sample_openapi_spec):
        """AC2: Generated code includes a happy-path test for POST /pets."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        assert "post" in code.lower()
        # The generated test should reference the /pets path for creation
        assert "/pets" in code

    def test_generated_code_has_get_pet_by_id_test(self, client, sample_openapi_spec):
        """AC2: Generated code includes a happy-path test for GET /pets/{petId}."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # Should reference the parameterized path
        assert "pet" in code.lower()

    def test_generated_code_covers_all_endpoints(self, client, sample_openapi_spec):
        """AC2: Every path in the spec has at least one corresponding test function."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        test_function_count = code.count("def test_")
        # The sample spec has 3 endpoint+method combos:
        #   GET /pets, POST /pets, GET /pets/{petId}
        # We expect at least 3 happy-path test functions (may be more with error tests)
        assert test_function_count >= 3, (
            f"Expected at least 3 test functions for 3 endpoints, "
            f"found {test_function_count}"
        )

    # -------------------------------------------------------------------
    # AC3: Schema validation tests
    # -------------------------------------------------------------------

    def test_generated_code_has_schema_validation(self, client, sample_openapi_spec):
        """AC3: Generated code includes jsonschema validation for endpoints with schemas.

        The sample spec defines response schemas for GET /pets and GET /pets/{petId},
        so the generated tests should include jsonschema validation calls.
        """
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # Should reference jsonschema validation (e.g., jsonschema.validate or validate())
        assert "jsonschema" in code.lower() or "validate" in code.lower(), (
            "Generated code should include schema validation "
            "(jsonschema.validate or similar)"
        )

    # -------------------------------------------------------------------
    # AC4: 404 tests for endpoints with path parameters
    # -------------------------------------------------------------------

    def test_generated_code_has_404_test_for_path_params(self, client, sample_openapi_spec):
        """AC4: Generated code includes a 404 test for GET /pets/{petId}.

        The spec defines a 404 response for the path-parameter endpoint,
        and the generator should produce a test that verifies 404 behaviour.
        """
        response = _generate(client, sample_openapi_spec)
        code = response.text
        assert "404" in code, (
            "Generated code should include a 404 status check "
            "for the path-parameter endpoint"
        )

    # -------------------------------------------------------------------
    # AC5: 422 tests for required request bodies
    # -------------------------------------------------------------------

    def test_generated_code_has_missing_body_test(self, client, sample_openapi_spec):
        """AC5: Generated code includes a 422 test for POST /pets (required body).

        The spec defines a required requestBody for POST /pets with a required
        'name' field. The generator should produce a test that sends a request
        with missing/empty body and expects 422.
        """
        response = _generate(client, sample_openapi_spec)
        code = response.text
        assert "422" in code, (
            "Generated code should include a 422 status check "
            "for endpoints with required request bodies"
        )

    # -------------------------------------------------------------------
    # AC9: Generated code is syntactically valid Python
    # -------------------------------------------------------------------

    def test_generated_code_compiles(self, client, sample_openapi_spec):
        """AC9: The generated test code is syntactically valid Python.

        Uses compile() to verify the code parses without SyntaxError.
        """
        response = _generate(client, sample_openapi_spec)
        code = response.text
        try:
            compile(code, "<generated>", "exec")
        except SyntaxError as exc:
            pytest.fail(
                f"Generated code is not valid Python: {exc}\n\n"
                f"--- Generated code ---\n{code}"
            )


# ---------------------------------------------------------------------------
# AC6: Invalid / non-OpenAPI JSON returns 400
# ---------------------------------------------------------------------------

class TestGenerateErrors:
    """Tests for POST /generate error handling."""

    def test_non_openapi_json_returns_400(self, client):
        """AC6: Sending valid JSON that is not an OpenAPI spec returns 400.

        A random JSON object without openapi/info/paths keys is not a valid
        OpenAPI spec and should be rejected with a descriptive error.
        """
        response = client.post(
            "/generate",
            json={"foo": "bar", "baz": 123},
        )
        assert response.status_code == 400

    def test_missing_paths_key_returns_400(self, client):
        """AC6: An object with openapi and info but no paths returns 400."""
        response = client.post(
            "/generate",
            json={
                "openapi": "3.0.0",
                "info": {"title": "Incomplete", "version": "1.0.0"},
            },
        )
        assert response.status_code == 400

    def test_missing_info_key_returns_400(self, client):
        """AC6: An object with openapi and paths but no info returns 400."""
        response = client.post(
            "/generate",
            json={
                "openapi": "3.0.0",
                "paths": {},
            },
        )
        assert response.status_code == 400

    def test_missing_openapi_key_returns_400(self, client):
        """AC6: An object with info and paths but no openapi version returns 400."""
        response = client.post(
            "/generate",
            json={
                "info": {"title": "No version", "version": "1.0.0"},
                "paths": {},
            },
        )
        assert response.status_code == 400

    def test_error_response_has_descriptive_message(self, client):
        """AC6: The 400 error response includes a descriptive error message."""
        response = client.post(
            "/generate",
            json={"not": "openapi"},
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body, (
            "Error response should include a 'detail' field with a message"
        )
        assert len(body["detail"]) > 0

    # -------------------------------------------------------------------
    # AC7: Missing or empty body returns 422
    # -------------------------------------------------------------------

    def test_empty_body_returns_422(self, client):
        """AC7: POST /generate with no body at all returns 422."""
        response = client.post("/generate")
        assert response.status_code == 422

    def test_empty_json_object_returns_error(self, client):
        """AC7: POST /generate with an empty JSON object returns 400 or 422.

        An empty dict {} is valid JSON but not an OpenAPI spec.
        The implementation may return 400 (not OpenAPI) or 422 (missing fields).
        Either is acceptable per the spec.
        """
        response = client.post("/generate", json={})
        assert response.status_code in (400, 422)

    def test_non_json_content_returns_422(self, client):
        """AC7: POST /generate with non-JSON content returns 422."""
        response = client.post(
            "/generate",
            content=b"this is not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# AC8: GET /health returns 200 with status "ok"
# ---------------------------------------------------------------------------

class TestHealth:
    """Tests for the GET /health endpoint."""

    def test_health_returns_200(self, client):
        """AC8: GET /health returns HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        """AC8: GET /health response body contains {"status": "ok"}."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_json(self, client):
        """AC8: GET /health returns JSON content type."""
        response = client.get("/health")
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type


# ---------------------------------------------------------------------------
# AC10: Swagger UI at /docs
# ---------------------------------------------------------------------------

class TestSwaggerUI:
    """Tests for Swagger UI availability."""

    def test_docs_accessible(self, client):
        """AC10: GET /docs returns 200."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_docs_returns_html(self, client):
        """AC10: GET /docs returns an HTML page (Swagger UI)."""
        response = client.get("/docs")
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type

    def test_docs_contains_swagger_ui(self, client):
        """AC10: The /docs page contains Swagger UI markers."""
        response = client.get("/docs")
        body = response.text
        assert "swagger" in body.lower() or "openapi" in body.lower(), (
            "/docs should serve Swagger UI with recognizable content"
        )


# ---------------------------------------------------------------------------
# Edge cases and additional coverage
# ---------------------------------------------------------------------------

class TestGenerateEdgeCases:
    """Edge-case and robustness tests for POST /generate."""

    def test_spec_with_no_paths_returns_200(self, client, minimal_openapi_spec):
        """Edge: A valid OpenAPI spec with an empty paths object still returns 200.

        The generator should handle specs with zero endpoints gracefully.
        """
        response = _generate(client, minimal_openapi_spec)
        assert response.status_code == 200

    def test_spec_with_no_paths_produces_valid_python(self, client, minimal_openapi_spec):
        """Edge: Even with no paths, the generated code should be valid Python."""
        response = _generate(client, minimal_openapi_spec)
        code = response.text
        try:
            compile(code, "<generated>", "exec")
        except SyntaxError as exc:
            pytest.fail(
                f"Generated code for empty-paths spec is invalid Python: {exc}\n\n"
                f"--- Generated code ---\n{code}"
            )

    def test_spec_with_multiple_methods_on_same_path(self, client, multi_method_spec):
        """Edge: A spec with GET, POST, and DELETE on /items generates tests for all.

        The multi_method_spec fixture has 3 methods on a single path.
        """
        response = _generate(client, multi_method_spec)
        code = response.text
        assert response.status_code == 200
        # Should produce at least one test per method
        test_count = code.count("def test_")
        assert test_count >= 3, (
            f"Expected at least 3 test functions for 3 methods on /items, "
            f"found {test_count}"
        )

    def test_generated_code_has_imports(self, client, sample_openapi_spec):
        """Edge: Generated code includes necessary import statements."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # At minimum should import requests or httpx (or similar HTTP library)
        has_http_import = (
            "import requests" in code
            or "import httpx" in code
            or "from requests" in code
            or "from httpx" in code
        )
        # Or it might use pytest's built-in client patterns
        has_pytest_import = "import pytest" in code or "from pytest" in code
        assert has_http_import or has_pytest_import, (
            "Generated code should include imports for HTTP calls or pytest"
        )

    def test_generated_code_has_base_url(self, client, sample_openapi_spec):
        """Edge: Generated code references a configurable base URL or host."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # The generated code should have some form of base URL configuration
        has_base_url = (
            "base_url" in code.lower()
            or "base" in code.lower()
            or "host" in code.lower()
            or "http://" in code
            or "https://" in code
        )
        assert has_base_url, (
            "Generated code should reference a base URL or host "
            "for the API under test"
        )

    def test_generated_code_uses_test_prefix(self, client, sample_openapi_spec):
        """Edge: All generated test functions follow pytest naming convention (test_ prefix)."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # Every function definition should use the test_ prefix
        import re
        func_names = re.findall(r"def (\w+)\(", code)
        test_funcs = [name for name in func_names if name.startswith("test_")]
        non_test_funcs = [
            name for name in func_names
            if not name.startswith("test_") and not name.startswith("_")
        ]
        assert len(test_funcs) > 0, "Generated code should contain test_ functions"
        # Helper functions (prefixed with _) are acceptable, but top-level
        # non-test, non-helper functions suggest incorrect naming
        for func in non_test_funcs:
            # Allow common helper/fixture patterns
            assert func in ("setup", "teardown", "fixture", "conftest"), (
                f"Unexpected non-test function '{func}' in generated code; "
                f"test functions should start with 'test_'"
            )

    def test_generated_code_has_assertions(self, client, sample_openapi_spec):
        """Edge: Generated tests contain assert statements for meaningful verification."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        assert "assert " in code, (
            "Generated test code must contain assert statements"
        )

    def test_generated_code_checks_status_codes(self, client, sample_openapi_spec):
        """Edge: Generated tests verify HTTP status codes from the spec."""
        response = _generate(client, sample_openapi_spec)
        code = response.text
        # The sample spec has 200, 201, and 404 status codes
        assert "200" in code, "Generated code should check for 200 status"
        assert "201" in code or "post" in code.lower(), (
            "Generated code should reference the 201 response for POST /pets"
        )
