# Feature Spec: Generated Code Conventions

## Goal
Define the format and conventions that all generated test code must follow, ensuring deterministic, readable, and pytest-compatible output.

## Scope
- In: Naming conventions for test functions, required imports, BASE_URL configuration, deterministic ordering of generated tests, test function patterns, name deduplication
- Out: Fixture generation, test parametrization, configurable base URL (environment variable or CLI flag), custom assertion helpers

## Requirements
- Generated test functions must use the `test_` prefix with snake_case names derived from the HTTP method and sanitized path
- Generated files must import `requests` and `from jsonschema import validate`
- Generated files must define a `BASE_URL` variable at module level so the target host is configurable in one place
- Endpoints must be sorted alphabetically by (path, method) so that output is deterministic across runs
- When multiple endpoints produce the same sanitized function base name, a numeric counter suffix (e.g., `_2`, `_3`) must be appended to keep names unique

## Acceptance Criteria
- [x] AC1: Generated functions use test_ prefix with snake_case names
- [x] AC2: Generated code includes requests and jsonschema imports
- [x] AC3: Generated code defines a configurable BASE_URL
- [x] AC4: Paths are sorted alphabetically for deterministic output
- [x] AC5: Function names are deduplicated with counters when paths collide
