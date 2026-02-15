"""Shared fixtures for tests."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture(autouse=True)
def temp_database(tmp_path):
    """Use a temporary database file for each test to ensure isolation."""
    db_file = str(tmp_path / "test.db")
    os.environ["APP_DB_PATH"] = db_file
    db.DB_PATH = db_file
    db.init_db()
    yield db_file
    # Cleanup is handled by tmp_path fixture


@pytest.fixture
def client():
    """Provide a FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def sample_test_case():
    """Return a sample test case payload for creating test cases."""
    return {
        "title": "Login with valid credentials",
        "description": "Verify that a user can log in with correct username and password",
        "steps": "1. Navigate to /login\n2. Enter valid username\n3. Enter valid password\n4. Click Submit",
        "expected_result": "User is redirected to the dashboard",
        "priority": "high",
        "status": "active",
        "tags": ["smoke", "regression"],
    }


@pytest.fixture
def created_test_case(client, sample_test_case):
    """Create a test case and return the response data."""
    response = client.post("/test-cases", json=sample_test_case)
    assert response.status_code == 201
    return response.json()
