# Test Case Manager API -- Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. Clone the repository and switch to the assessment branch:

```bash
git checkout adam-smith-assessment
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python run.py
```

The server will start on `http://0.0.0.0:8000`.

## Swagger UI

Once the server is running, open the interactive API documentation:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Running Tests

```bash
pytest -v
```

Tests use isolated temporary SQLite databases, so they will not affect any production data.

## API Endpoints

| Method | Endpoint              | Description                          |
|--------|-----------------------|--------------------------------------|
| POST   | `/test-cases`         | Create a new test case               |
| GET    | `/test-cases`         | List all test cases (with filters)   |
| GET    | `/test-cases/{id}`    | Get a test case by ID                |
| PUT    | `/test-cases/{id}`    | Update a test case                   |
| DELETE | `/test-cases/{id}`    | Delete a test case                   |

### Query Parameters for GET /test-cases

| Parameter  | Type   | Description            |
|------------|--------|------------------------|
| `status`   | string | Filter by status (active, inactive, draft) |
| `priority` | string | Filter by priority (low, medium, high, critical) |
| `tag`      | string | Filter by tag          |
