"""Tests for task API endpoints."""

import json


def _create_project(client):
    """Helper to create a project and return its ID."""
    res = client.post("/api/projects",
        data=json.dumps({"name": "Task Test Project"}),
        content_type="application/json")
    return res.get_json()["data"]["id"]


def test_create_task(client):
    """Test creating a task in a project."""
    pid = _create_project(client)
    response = client.post(f"/api/projects/{pid}/tasks",
        data=json.dumps({"title": "My Task", "priority": "high"}),
        content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["title"] == "My Task"
    assert data["priority"] == "high"


def test_create_task_missing_title(client):
    """Test creating task without title returns 400."""
    pid = _create_project(client)
    response = client.post(f"/api/projects/{pid}/tasks",
        data=json.dumps({"description": "No title"}),
        content_type="application/json")
    assert response.status_code == 400


def test_create_task_invalid_priority(client):
    """Test creating task with invalid priority returns 400."""
    pid = _create_project(client)
    response = client.post(f"/api/projects/{pid}/tasks",
        data=json.dumps({"title": "T", "priority": "ultra"}),
        content_type="application/json")
    assert response.status_code == 400


def test_create_task_nonexistent_project(client):
    """Test creating task in nonexistent project returns 404."""
    response = client.post("/api/projects/fake_id/tasks",
        data=json.dumps({"title": "Orphan"}),
        content_type="application/json")
    assert response.status_code == 404
