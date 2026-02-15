# TODO

## Completed

- [x] Test Case Manager API (see SPECS/test-case-manager-api.md)
  - [x] AC1: POST /test-cases creates a test case and returns 201
  - [x] AC2: GET /test-cases returns all test cases as a list with 200
  - [x] AC3: GET /test-cases?status=active filters by status
  - [x] AC4: GET /test-cases?priority=high filters by priority
  - [x] AC5: GET /test-cases?tag=regression filters by tag
  - [x] AC6: GET /test-cases/{id} returns a single test case with 200
  - [x] AC7: GET /test-cases/{id} returns 404 for non-existent ID
  - [x] AC8: PUT /test-cases/{id} updates the test case and returns 200
  - [x] AC9: PUT /test-cases/{id} returns 404 for non-existent ID
  - [x] AC10: DELETE /test-cases/{id} deletes the test case and returns 200
  - [x] AC11: DELETE /test-cases/{id} returns 404 for non-existent ID
  - [x] AC12: POST /test-cases with invalid data returns 422
  - [x] AC13: Swagger UI is accessible at /docs
  - [x] AC14: Data persists across server restarts (SQLite)

## Refactor Proposals

-

## New Feature Proposals

-
