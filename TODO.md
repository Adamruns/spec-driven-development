# TODO

## Completed

- [x] Spec-to-Test Generator API (see SPECS/spec-to-test-generator.md)
  - [x] AC1: POST /generate returns 200 with generated pytest code
  - [x] AC2: Generated tests include happy-path tests for each endpoint
  - [x] AC3: Generated tests include jsonschema response validation
  - [x] AC4: Generated tests include 404 tests for path-parameter endpoints
  - [x] AC5: Generated tests include 422 tests for required request body fields
  - [x] AC6: Invalid/non-OpenAPI JSON returns 400
  - [x] AC7: Missing or empty body returns 422
  - [x] AC8: GET /health returns 200
  - [x] AC9: Generated code is syntactically valid Python
  - [x] AC10: Swagger UI accessible at /docs

- [x] Input Validation and Error Handling (see SPECS/input-validation-and-error-handling.md)
  - [x] AC1: OpenAPI 2.0 spec rejected with 400
  - [x] AC2: Non-object `paths` rejected with 400
  - [x] AC3: Missing required keys rejected with 400
  - [x] AC4: Non-JSON body returns 422
  - [x] AC5: Empty body returns 422
  - [x] AC6: All errors include descriptive `detail` field

## Refactor Proposals

-

## New Feature Proposals

-
