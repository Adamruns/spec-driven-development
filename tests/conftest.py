"""Shared fixtures for Spec-to-Test Generator API tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for the application."""
    return TestClient(app)


@pytest.fixture
def sample_openapi_spec():
    """A minimal but valid OpenAPI 3.x spec for testing.

    Includes multiple endpoints, path parameters, request bodies,
    response schemas, and various HTTP methods to exercise all
    generation paths.
    """
    return {
        "openapi": "3.0.0",
        "info": {"title": "Pet Store", "version": "1.0.0"},
        "paths": {
            "/pets": {
                "get": {
                    "summary": "List pets",
                    "responses": {
                        "200": {
                            "description": "A list of pets",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a pet",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "tag": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Pet created"}
                    },
                },
            },
            "/pets/{petId}": {
                "get": {
                    "summary": "Get a pet",
                    "parameters": [
                        {
                            "name": "petId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A pet",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "Pet not found"},
                    },
                }
            },
        },
    }


@pytest.fixture
def minimal_openapi_spec():
    """The smallest valid OpenAPI spec: required keys present but paths is empty."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Empty API", "version": "0.1.0"},
        "paths": {},
    }


@pytest.fixture
def multi_method_spec():
    """An OpenAPI spec with multiple HTTP methods on a single path."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Multi-Method API", "version": "1.0.0"},
        "paths": {
            "/items": {
                "get": {
                    "summary": "List items",
                    "responses": {
                        "200": {"description": "A list of items"}
                    },
                },
                "post": {
                    "summary": "Create an item",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                    "properties": {
                                        "name": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Item created"}
                    },
                },
                "delete": {
                    "summary": "Delete all items",
                    "responses": {
                        "204": {"description": "All items deleted"}
                    },
                },
            }
        },
    }
