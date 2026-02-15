# Feature Spec: Spec-to-Test Generator

## Goal
Provide a REST API that accepts an OpenAPI 3.x specification and generates a runnable pytest test suite covering happy paths, error cases, and schema validation.

## Scope
- In: Parse OpenAPI 3.x JSON specs, generate pytest test code, REST API, health endpoint, Swagger UI
- Out: YAML spec parsing, `$ref` resolution, authentication test generation, performance testing, UI/frontend

## Requirements
- POST /generate accepts an OpenAPI 3.x JSON spec in the request body and returns generated pytest code as a text string
- GET /health returns a simple health check response
- Generated tests cover:
  - Happy-path request for each endpoint (correct method + expected status code)
  - Response schema validation using jsonschema where response schemas are defined
  - Error-path tests: 404 for endpoints with path parameters, 422 for endpoints with required request bodies (missing fields)
- Generated code must be syntactically valid Python importable by pytest
- Generated code follows pytest conventions (test_ prefix functions, clear assertions)
- Swagger UI available at /docs

## Acceptance Criteria
- [x] AC1: POST /generate with a valid OpenAPI spec returns 200 with generated pytest code
- [x] AC2: Generated tests include a happy-path test for each endpoint+method in the spec
- [x] AC3: Generated tests include jsonschema validation for endpoints with defined response schemas
- [x] AC4: Generated tests include 404 tests for endpoints with path parameters
- [x] AC5: Generated tests include 422 tests for endpoints with explicitly required request bodies
- [x] AC6: POST /generate with invalid/non-OpenAPI JSON returns 400 with a descriptive error message (see also SPECS/input-validation-and-error-handling.md)
- [x] AC7: POST /generate with missing or empty body returns 422
- [x] AC8: GET /health returns 200 with status "ok"
- [x] AC9: Generated test code is syntactically valid Python (compiles without errors)
- [x] AC10: Swagger UI is accessible at /docs
