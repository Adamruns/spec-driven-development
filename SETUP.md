# Spec-to-Test Generator API -- Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. Clone the repository and switch to the assessment branch:

```bash
git checkout adam-smith-assessment
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies: fastapi, uvicorn, pydantic, pytest, httpx

## Running the Server

```bash
python run.py
```

The server starts on `http://localhost:8000`. Swagger UI is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Endpoints

| Method | Endpoint     | Description                                                        |
|--------|--------------|--------------------------------------------------------------------|
| POST   | `/generate`  | Accept an OpenAPI 3.x spec (JSON) and return generated pytest code |
| GET    | `/health`    | Health check                                                       |

## Example Usage

Send an OpenAPI spec to the `/generate` endpoint and receive a generated pytest test suite:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "openapi": "3.0.0",
    "info": { "title": "Sample API", "version": "1.0.0" },
    "paths": {
      "/users": {
        "get": {
          "summary": "List users",
          "responses": { "200": { "description": "OK" } }
        }
      }
    }
  }'
```

The response body contains the generated pytest code as a string.

## Running Tests

```bash
pytest -v
```
