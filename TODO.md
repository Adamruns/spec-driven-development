# TODO

## Refactor Proposals

- Use a Pydantic request model for `/generate` instead of raw `Request` parsing
- Extract inline schema dicts in generated code to module-level constants for readability

## New Feature Proposals

- `$ref` resolution: inline `components/schemas` references before generating tests
- YAML input support: accept `application/x-yaml` content type alongside JSON
- Authentication test generation: API key, Bearer token, and OAuth2 flows
- Configurable `BASE_URL` in generated output via environment variable
- Richer generated patterns: `conftest.py` with fixtures, `@pytest.mark.parametrize` for invalid payloads
