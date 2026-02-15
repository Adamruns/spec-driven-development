# Feature Spec: Input Validation and Error Handling

## Goal
Ensure the `/generate` endpoint robustly validates incoming requests, returning clear error responses for malformed, invalid, or unsupported input rather than crashing or producing incorrect output.

## Scope
- In: OpenAPI version validation, `paths` type validation, missing/malformed JSON handling, descriptive error messages
- Out: Full OpenAPI schema validation (e.g. validating every field in the spec), rate limiting, payload size limits

## Requirements
- POST /generate rejects non-3.x OpenAPI specs with 400 and a message naming the unsupported version
- POST /generate rejects specs where `paths` is not a JSON object with 400
- POST /generate rejects JSON payloads missing required OpenAPI keys (`openapi`, `info`, `paths`) with 400 and lists the missing keys
- POST /generate rejects non-JSON and empty request bodies with 422
- All error responses include a `detail` field with a human-readable message

## Acceptance Criteria
- [x] AC1: POST /generate with an OpenAPI 2.0 spec returns 400 mentioning version support
- [x] AC2: POST /generate with `paths` as a list returns 400 mentioning `paths`
- [x] AC3: POST /generate with missing `openapi`, `info`, or `paths` keys returns 400 listing the missing keys
- [x] AC4: POST /generate with non-JSON body returns 422
- [x] AC5: POST /generate with empty body returns 422
- [x] AC6: All 400/422 responses include a `detail` field with a descriptive message
