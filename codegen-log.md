# Code Generation Log

This document records how AI tools were used during development of the Spec-to-Test Generator.

## Tools Used

- **Claude Code** (Anthropic) — Primary development tool for implementation, testing, and iterative refinement
- **OpenAI Codex** — Independent cross-check of generator logic and test coverage

## Development Timeline

### Phase 1: Concept and Spec Design
- Used Claude Code to brainstorm application concepts that go beyond a basic CRUD app
- Initially explored a Test Case Manager (CRUD API for QA test cases), then pivoted to the Spec-to-Test Generator after recognizing it was more aligned with the assessment's spec-driven philosophy
- Wrote `SPECS/spec-to-test-generator.md` with 10 acceptance criteria before any implementation code

### Phase 2: Core Generator Implementation
- Claude Code generated the initial `generator.py` with the core `generate_test_code()` function
- Manual review identified that `json.dumps()` was producing `true`/`false`/`null` (JSON literals) instead of Python's `True`/`False`/`None` in generated code — switched to `repr()` for Python-native output
- Iteratively refined path sanitization (`_sanitize_path_for_name`) to handle camelCase path parameters, hyphens, and nested paths correctly

### Phase 3: Input Validation and Error Handling
- Wrote `SPECS/input-validation-and-error-handling.md` before implementing validation logic
- Claude Code generated the layered validation in `main.py` (JSON parse → dict check → required keys → version → paths type)
- Codex independently flagged that OpenAPI 2.0 specs and malformed `paths` values (arrays instead of dicts) were not handled — both error paths added

### Phase 4: Generated Code Conventions
- Wrote `SPECS/generated-code-conventions.md` to codify output format decisions
- Key decisions made during this phase:
  - Deterministic output: paths sorted by `(path, method)`, function names deduplicated with counters
  - `$ref` detection: skip schema validation for referenced schemas rather than producing broken `validate()` calls
  - `requestBody.required` honored: missing-body tests only generated when explicitly required per OpenAPI 3.x spec

### Phase 5: Test Suite and Refinement
- Built two-tier test suite: 40 unit tests for generator internals, 36 integration tests mapped to acceptance criteria
- Claude Code review agent caught that `$ref` schemas were leaking into generated output as raw `{"$ref": "..."}` dicts — added `_contains_ref()` guard
- Added smoke test that writes generated code to a temp file and runs `pytest --collect-only` to verify structural validity
- Codex cross-check confirmed test coverage aligned with all 21 acceptance criteria

## What the AI Got Wrong (and How It Was Fixed)

| Issue | Tool | How Caught | Fix |
|-------|------|-----------|-----|
| `json.dumps` producing JSON booleans in Python code | Claude Code | Manual review of generated output | Switched to `repr()` for Python literals |
| `$ref` schemas leaking into generated `validate()` calls | Claude Code | Review agent | Added `_contains_ref()` to skip schema validation for `$ref` specs |
| No OpenAPI 2.0 version check | Codex | Cross-check session | Added version validation in `main.py` |
| `paths` as array didn't raise clear error | Codex | Cross-check session | Added `isinstance(paths, dict)` check |
| Initial concept (Test Case Manager) was generic | Claude Code | Self-assessment | Pivoted to Spec-to-Test Generator |
