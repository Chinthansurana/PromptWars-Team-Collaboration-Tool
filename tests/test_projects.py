"""Tests for project API endpoints."""

import json


def test_create_project(client):
    """Test creating a new project."""
    response = client.post("/api/projects",
        data=json.dumps({"name": "Test Project", "description": "A test", "members": ["Alice"]}),
        content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["name"] == "Test Project"
    assert "id" in data["data"]


def test_create_project_missing_name(client):
    """Test creating project without name returns 400."""
    response = client.post("/api/projects",
        data=json.dumps({"description": "No name"}),
        content_type="application/json")
    assert response.status_code == 400


def test_list_projects(client):
    """Test listing projects."""
    client.post("/api/projects",
        data=json.dumps({"name": "P1"}),
        content_type="application/json")
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data["data"], list)


def test_get_project_not_found(client):
    """Test getting a non-existent project returns 404."""
    response = client.get("/api/projects/nonexistent")
    assert response.status_code == 404


def test_delete_project_not_found(client):
    """Test deleting a non-existent project returns 404."""
    response = client.delete("/api/projects/nonexistent")
    assert response.status_code == 404


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"
