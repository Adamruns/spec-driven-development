"""Unit tests for generator.py internals.

These tests exercise the helper functions in app/generator.py directly,
without going through the HTTP API layer. Each test targets a single
function to ensure correctness of path sanitization, schema sampling,
response parsing, name deduplication, and full spec parsing.
"""

import pytest

from app.generator import (
    _contains_ref,
    _generate_sample_value,
    _get_lowest_2xx_status,
    _get_response_schema,
    _has_path_params,
    _has_required_request_body,
    _make_path_with_nonexistent_values,
    _make_path_with_sample_values,
    _sanitize_path_for_name,
    _unique_name,
    parse_openapi_spec,
)


# ---------------------------------------------------------------------------
# _sanitize_path_for_name
# ---------------------------------------------------------------------------

class TestSanitizePathForName:

    def test_simple_path(self):
        assert _sanitize_path_for_name("/pets") == "pets"

    def test_path_with_param(self):
        assert _sanitize_path_for_name("/pets/{petId}") == "pets_pet_id"

    def test_nested_path_with_params(self):
        result = _sanitize_path_for_name("/users/{userId}/posts")
        assert result == "users_user_id_posts"

    def test_strips_leading_and_trailing_slashes(self):
        assert _sanitize_path_for_name("/items/") == "items"

    def test_hyphens_become_underscores(self):
        assert _sanitize_path_for_name("/pet-store") == "pet_store"


# ---------------------------------------------------------------------------
# _has_path_params
# ---------------------------------------------------------------------------

class TestHasPathParams:

    def test_path_without_params(self):
        assert _has_path_params("/pets") is False

    def test_path_with_param(self):
        assert _has_path_params("/pets/{petId}") is True

    def test_path_with_multiple_params(self):
        assert _has_path_params("/users/{userId}/posts/{postId}") is True


# ---------------------------------------------------------------------------
# _get_lowest_2xx_status
# ---------------------------------------------------------------------------

class TestGetLowest2xxStatus:

    def test_single_200(self):
        assert _get_lowest_2xx_status({"200": {}}) == 200

    def test_multiple_2xx_returns_lowest(self):
        assert _get_lowest_2xx_status({"201": {}, "200": {}, "204": {}}) == 200

    def test_no_2xx_falls_back_to_200(self):
        assert _get_lowest_2xx_status({"404": {}, "500": {}}) == 200

    def test_non_numeric_keys_ignored(self):
        assert _get_lowest_2xx_status({"default": {}, "201": {}}) == 201


# ---------------------------------------------------------------------------
# _generate_sample_value
# ---------------------------------------------------------------------------

class TestGenerateSampleValue:

    def test_string(self):
        assert _generate_sample_value({"type": "string"}) == "string"

    def test_integer(self):
        assert _generate_sample_value({"type": "integer"}) == 1

    def test_number(self):
        assert _generate_sample_value({"type": "number"}) == 1.0

    def test_boolean(self):
        assert _generate_sample_value({"type": "boolean"}) is True

    def test_array(self):
        result = _generate_sample_value({"type": "array", "items": {"type": "integer"}})
        assert result == [1]

    def test_object_with_properties(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        result = _generate_sample_value(schema)
        assert result == {"name": "string", "age": 1}

    def test_enum_returns_first_value(self):
        schema = {"type": "string", "enum": ["active", "inactive"]}
        assert _generate_sample_value(schema) == "active"

    def test_none_schema_returns_empty_dict(self):
        assert _generate_sample_value(None) == {}


# ---------------------------------------------------------------------------
# _contains_ref
# ---------------------------------------------------------------------------

class TestContainsRef:

    def test_no_ref(self):
        assert _contains_ref({"type": "object"}) is False

    def test_top_level_ref(self):
        assert _contains_ref({"$ref": "#/components/schemas/Pet"}) is True

    def test_nested_ref(self):
        schema = {
            "type": "object",
            "properties": {
                "pet": {"$ref": "#/components/schemas/Pet"},
            },
        }
        assert _contains_ref(schema) is True

    def test_ref_in_array(self):
        schema = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/Pet"},
        }
        assert _contains_ref(schema) is True


# ---------------------------------------------------------------------------
# _has_required_request_body
# ---------------------------------------------------------------------------

class TestHasRequiredRequestBody:

    def test_no_request_body(self):
        assert _has_required_request_body({"responses": {}}) is False

    def test_optional_request_body(self):
        op = {
            "requestBody": {
                "content": {"application/json": {"schema": {}}},
            },
        }
        assert _has_required_request_body(op) is False

    def test_required_request_body(self):
        op = {
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {}}},
            },
        }
        assert _has_required_request_body(op) is True


# ---------------------------------------------------------------------------
# _make_path_with_sample_values / _make_path_with_nonexistent_values
# ---------------------------------------------------------------------------

class TestPathSubstitution:

    def test_sample_values_replaces_param(self):
        assert _make_path_with_sample_values("/pets/{petId}") == "/pets/1"

    def test_sample_values_multiple_params(self):
        result = _make_path_with_sample_values("/users/{userId}/posts/{postId}")
        assert result == "/users/1/posts/1"

    def test_nonexistent_values_replaces_param(self):
        assert _make_path_with_nonexistent_values("/pets/{petId}") == "/pets/999999"

    def test_nonexistent_values_multiple_params(self):
        result = _make_path_with_nonexistent_values("/users/{userId}/posts/{postId}")
        assert result == "/users/999999/posts/999999"


# ---------------------------------------------------------------------------
# _unique_name
# ---------------------------------------------------------------------------

class TestUniqueName:

    def test_first_name_is_unchanged(self):
        seen = set()
        assert _unique_name("get_pets", seen) == "get_pets"
        assert "get_pets" in seen

    def test_duplicate_gets_counter(self):
        seen = {"get_pets"}
        assert _unique_name("get_pets", seen) == "get_pets_2"

    def test_triple_duplicate(self):
        seen = {"get_pets", "get_pets_2"}
        assert _unique_name("get_pets", seen) == "get_pets_3"


# ---------------------------------------------------------------------------
# _get_response_schema
# ---------------------------------------------------------------------------

class TestGetResponseSchema:

    def test_extracts_json_schema(self):
        responses = {
            "200": {
                "description": "OK",
                "content": {
                    "application/json": {
                        "schema": {"type": "object"},
                    },
                },
            },
        }
        assert _get_response_schema(responses, 200) == {"type": "object"}

    def test_returns_none_when_no_schema(self):
        responses = {"200": {"description": "OK"}}
        assert _get_response_schema(responses, 200) is None

    def test_returns_none_for_ref_schema(self):
        responses = {
            "200": {
                "description": "OK",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Pet"},
                    },
                },
            },
        }
        assert _get_response_schema(responses, 200) is None


# ---------------------------------------------------------------------------
# parse_openapi_spec
# ---------------------------------------------------------------------------

class TestParseOpenapiSpec:

    def test_parses_endpoints(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/pets": {
                    "get": {
                        "responses": {"200": {"description": "OK"}},
                    },
                },
                "/pets/{petId}": {
                    "get": {
                        "responses": {"200": {"description": "OK"}},
                    },
                },
            },
        }
        endpoints = parse_openapi_spec(spec)
        assert len(endpoints) == 2
        assert endpoints[0]["path"] == "/pets"
        assert endpoints[0]["method"] == "get"
        assert endpoints[1]["path"] == "/pets/{petId}"
        assert endpoints[1]["has_path_params"] is True

    def test_returns_sorted_by_path(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/zebras": {"get": {"responses": {"200": {}}}},
                "/ants": {"get": {"responses": {"200": {}}}},
            },
        }
        endpoints = parse_openapi_spec(spec)
        assert endpoints[0]["path"] == "/ants"
        assert endpoints[1]["path"] == "/zebras"

    def test_empty_paths(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        assert parse_openapi_spec(spec) == []
