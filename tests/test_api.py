"""API tests for the Test Case Manager.

Tests are mapped to Acceptance Criteria in SPECS/test-case-manager-api.md.
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# AC1: POST /test-cases creates a test case and returns 201
# ---------------------------------------------------------------------------

class TestCreateTestCase:
    """Tests for POST /test-cases."""

    def test_create_test_case_returns_201(self, client, sample_test_case):
        """AC1: POST /test-cases returns 201 with the created resource."""
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 201

    def test_create_test_case_returns_created_resource(self, client, sample_test_case):
        """AC1: The response body contains the created test case with an id."""
        response = client.post("/test-cases", json=sample_test_case)
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_test_case["title"]
        assert data["description"] == sample_test_case["description"]
        assert data["steps"] == sample_test_case["steps"]
        assert data["expected_result"] == sample_test_case["expected_result"]
        assert data["priority"] == sample_test_case["priority"]
        assert data["status"] == sample_test_case["status"]
        assert data["tags"] == sample_test_case["tags"]

    def test_create_test_case_has_timestamps(self, client, sample_test_case):
        """AC1: The created test case includes created_at and updated_at."""
        response = client.post("/test-cases", json=sample_test_case)
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_test_case_with_empty_tags(self, client, sample_test_case):
        """Test that creating a test case with no tags works."""
        sample_test_case["tags"] = []
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 201
        assert response.json()["tags"] == []

    def test_create_test_case_auto_increments_id(self, client, sample_test_case):
        """Test that IDs are auto-incremented."""
        r1 = client.post("/test-cases", json=sample_test_case)
        r2 = client.post("/test-cases", json=sample_test_case)
        assert r2.json()["id"] == r1.json()["id"] + 1


# ---------------------------------------------------------------------------
# AC2: GET /test-cases returns all test cases
# ---------------------------------------------------------------------------

class TestListTestCases:
    """Tests for GET /test-cases."""

    def test_list_test_cases_returns_200(self, client):
        """AC2: GET /test-cases returns 200."""
        response = client.get("/test-cases")
        assert response.status_code == 200

    def test_list_test_cases_returns_list(self, client):
        """AC2: GET /test-cases returns a list."""
        response = client.get("/test-cases")
        assert isinstance(response.json(), list)

    def test_list_empty_returns_empty_list(self, client):
        """Extra: When no test cases exist, returns an empty list."""
        response = client.get("/test-cases")
        assert response.json() == []

    def test_list_returns_all_created(self, client, sample_test_case):
        """AC2: All created test cases appear in the list."""
        client.post("/test-cases", json=sample_test_case)
        sample_test_case["title"] = "Another test case"
        client.post("/test-cases", json=sample_test_case)
        response = client.get("/test-cases")
        assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# AC3-AC5: Filtering
# ---------------------------------------------------------------------------

class TestFilterTestCases:
    """Tests for GET /test-cases with query filters."""

    def test_filter_by_status(self, client, sample_test_case):
        """AC3: GET /test-cases?status=active filters by status."""
        # Create an active test case
        client.post("/test-cases", json=sample_test_case)
        # Create a draft test case
        draft = sample_test_case.copy()
        draft["status"] = "draft"
        draft["title"] = "Draft test case"
        client.post("/test-cases", json=draft)

        response = client.get("/test-cases", params={"status": "active"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"

    def test_filter_by_priority(self, client, sample_test_case):
        """AC4: GET /test-cases?priority=high filters by priority."""
        client.post("/test-cases", json=sample_test_case)
        low = sample_test_case.copy()
        low["priority"] = "low"
        low["title"] = "Low priority test"
        client.post("/test-cases", json=low)

        response = client.get("/test-cases", params={"priority": "high"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"

    def test_filter_by_tag(self, client, sample_test_case):
        """AC5: GET /test-cases?tag=regression filters by tag."""
        client.post("/test-cases", json=sample_test_case)
        no_regression = sample_test_case.copy()
        no_regression["tags"] = ["smoke"]
        no_regression["title"] = "Smoke only"
        client.post("/test-cases", json=no_regression)

        response = client.get("/test-cases", params={"tag": "regression"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "regression" in data[0]["tags"]

    def test_filter_by_multiple_params(self, client, sample_test_case):
        """Extra: Filter by status and priority simultaneously."""
        client.post("/test-cases", json=sample_test_case)

        other = sample_test_case.copy()
        other["status"] = "draft"
        other["priority"] = "low"
        other["title"] = "Draft low"
        client.post("/test-cases", json=other)

        response = client.get(
            "/test-cases", params={"status": "active", "priority": "high"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"
        assert data[0]["priority"] == "high"

    def test_filter_returns_empty_when_no_match(self, client, sample_test_case):
        """Extra: Filtering with no matches returns an empty list."""
        client.post("/test-cases", json=sample_test_case)
        response = client.get("/test-cases", params={"status": "inactive"})
        assert response.status_code == 200
        assert response.json() == []


# ---------------------------------------------------------------------------
# AC6-AC7: GET /test-cases/{id}
# ---------------------------------------------------------------------------

class TestGetTestCaseById:
    """Tests for GET /test-cases/{id}."""

    def test_get_by_id_returns_200(self, client, created_test_case):
        """AC6: GET /test-cases/{id} returns 200 for an existing test case."""
        tc_id = created_test_case["id"]
        response = client.get(f"/test-cases/{tc_id}")
        assert response.status_code == 200

    def test_get_by_id_returns_correct_data(self, client, created_test_case):
        """AC6: The returned data matches what was created."""
        tc_id = created_test_case["id"]
        response = client.get(f"/test-cases/{tc_id}")
        data = response.json()
        assert data["id"] == tc_id
        assert data["title"] == created_test_case["title"]

    def test_get_nonexistent_returns_404(self, client):
        """AC7: GET /test-cases/{id} returns 404 for a non-existent ID."""
        response = client.get("/test-cases/99999")
        assert response.status_code == 404

    def test_create_and_get_by_id(self, client, sample_test_case):
        """Extra: End-to-end create then retrieve by ID."""
        create_resp = client.post("/test-cases", json=sample_test_case)
        assert create_resp.status_code == 201
        tc_id = create_resp.json()["id"]

        get_resp = client.get(f"/test-cases/{tc_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == sample_test_case["title"]
        assert get_resp.json()["tags"] == sample_test_case["tags"]


# ---------------------------------------------------------------------------
# AC8-AC9: PUT /test-cases/{id}
# ---------------------------------------------------------------------------

class TestUpdateTestCase:
    """Tests for PUT /test-cases/{id}."""

    def test_update_returns_200(self, client, created_test_case):
        """AC8: PUT /test-cases/{id} returns 200 on successful update."""
        tc_id = created_test_case["id"]
        response = client.put(
            f"/test-cases/{tc_id}", json={"title": "Updated title"}
        )
        assert response.status_code == 200

    def test_update_changes_field(self, client, created_test_case):
        """AC8: The updated field is reflected in the response."""
        tc_id = created_test_case["id"]
        response = client.put(
            f"/test-cases/{tc_id}", json={"title": "Updated title"}
        )
        assert response.json()["title"] == "Updated title"

    def test_update_preserves_other_fields(self, client, created_test_case):
        """AC8: Fields not included in the update remain unchanged."""
        tc_id = created_test_case["id"]
        response = client.put(
            f"/test-cases/{tc_id}", json={"title": "Updated title"}
        )
        data = response.json()
        assert data["description"] == created_test_case["description"]
        assert data["priority"] == created_test_case["priority"]

    def test_update_changes_updated_at(self, client, created_test_case):
        """AC8: The updated_at timestamp changes after an update."""
        tc_id = created_test_case["id"]
        original_updated_at = created_test_case["updated_at"]

        import time
        time.sleep(0.01)  # Ensure timestamp difference

        response = client.put(
            f"/test-cases/{tc_id}", json={"title": "Updated title"}
        )
        assert response.json()["updated_at"] != original_updated_at

    def test_update_nonexistent_returns_404(self, client):
        """AC9: PUT /test-cases/{id} returns 404 for a non-existent ID."""
        response = client.put(
            "/test-cases/99999", json={"title": "Does not exist"}
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# AC10-AC11: DELETE /test-cases/{id}
# ---------------------------------------------------------------------------

class TestDeleteTestCase:
    """Tests for DELETE /test-cases/{id}."""

    def test_delete_returns_200(self, client, created_test_case):
        """AC10: DELETE /test-cases/{id} returns 200 on successful deletion."""
        tc_id = created_test_case["id"]
        response = client.delete(f"/test-cases/{tc_id}")
        assert response.status_code == 200

    def test_delete_removes_test_case(self, client, created_test_case):
        """AC10: After deletion, the test case is no longer retrievable."""
        tc_id = created_test_case["id"]
        client.delete(f"/test-cases/{tc_id}")
        response = client.get(f"/test-cases/{tc_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        """AC11: DELETE /test-cases/{id} returns 404 for a non-existent ID."""
        response = client.delete("/test-cases/99999")
        assert response.status_code == 404

    def test_delete_then_get_returns_404(self, client, created_test_case):
        """Extra: Delete a test case, then verify GET returns 404."""
        tc_id = created_test_case["id"]
        del_resp = client.delete(f"/test-cases/{tc_id}")
        assert del_resp.status_code == 200

        get_resp = client.get(f"/test-cases/{tc_id}")
        assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# AC12: Validation errors
# ---------------------------------------------------------------------------

class TestValidation:
    """Tests for input validation (422 errors)."""

    def test_create_missing_required_fields_returns_422(self, client):
        """AC12: POST /test-cases with missing required fields returns 422."""
        response = client.post("/test-cases", json={})
        assert response.status_code == 422

    def test_create_empty_title_returns_422(self, client, sample_test_case):
        """AC12: POST /test-cases with an empty title returns 422."""
        sample_test_case["title"] = ""
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 422

    def test_create_invalid_priority_returns_422(self, client, sample_test_case):
        """AC12: POST /test-cases with an invalid priority returns 422."""
        sample_test_case["priority"] = "urgent"
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 422

    def test_create_invalid_status_returns_422(self, client, sample_test_case):
        """AC12: POST /test-cases with an invalid status returns 422."""
        sample_test_case["status"] = "archived"
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 422

    def test_create_missing_title_returns_422(self, client, sample_test_case):
        """AC12: POST /test-cases without a title field returns 422."""
        del sample_test_case["title"]
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 422

    def test_create_missing_description_returns_422(self, client, sample_test_case):
        """AC12: POST /test-cases without a description field returns 422."""
        del sample_test_case["description"]
        response = client.post("/test-cases", json=sample_test_case)
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# AC13: Swagger UI
# ---------------------------------------------------------------------------

class TestSwaggerUI:
    """Tests for Swagger UI availability."""

    def test_swagger_ui_accessible(self, client):
        """AC13: Swagger UI is accessible at /docs."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# AC14: Persistence (SQLite)
# ---------------------------------------------------------------------------

class TestPersistence:
    """Tests for data persistence."""

    def test_data_persists_across_client_sessions(self, client, sample_test_case):
        """AC14: Data persists in SQLite (survives new client instances)."""
        # Create a test case
        create_resp = client.post("/test-cases", json=sample_test_case)
        assert create_resp.status_code == 201
        tc_id = create_resp.json()["id"]

        # Create a new client (simulating a restart, same DB file)
        from app.main import app as the_app
        new_client = TestClient(the_app)

        # The test case should still be there
        get_resp = new_client.get(f"/test-cases/{tc_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == sample_test_case["title"]
