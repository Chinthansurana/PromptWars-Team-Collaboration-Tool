"""Tests for AI endpoints."""

import json
from unittest.mock import MagicMock, patch


def _create_project(client):
    res = client.post("/api/projects",
        data=json.dumps({"name": "AI Test", "description": "Test AI features"}),
        content_type="application/json")
    return res.get_json()["data"]["id"]


@patch("app.services.gemini_service.get_client")
def test_summarize(mock_client, client):
    """Test AI summarize endpoint."""
    pid = _create_project(client)
    mock_response = MagicMock()
    mock_response.text = "## Summary\nAll good!"
    mock_client.return_value.models.generate_content.return_value = mock_response

    response = client.post("/api/ai/summarize",
        data=json.dumps({"project_id": pid}),
        content_type="application/json")
    assert response.status_code == 200


@patch("app.services.gemini_service.get_client")
def test_suggest_tasks(mock_client, client):
    """Test AI suggest tasks endpoint."""
    pid = _create_project(client)
    mock_response = MagicMock()
    mock_response.text = '[{"title": "Setup", "priority": "high"}]'
    mock_client.return_value.models.generate_content.return_value = mock_response

    response = client.post("/api/ai/suggest-tasks",
        data=json.dumps({"project_id": pid}),
        content_type="application/json")
    assert response.status_code == 200


def test_summarize_missing_project(client):
    """Test summarize without project_id returns 400."""
    response = client.post("/api/ai/summarize",
        data=json.dumps({}),
        content_type="application/json")
    assert response.status_code == 400


def test_summarize_nonexistent_project(client):
    """Test summarize with fake project returns 404."""
    response = client.post("/api/ai/summarize",
        data=json.dumps({"project_id": "fake"}),
        content_type="application/json")
    assert response.status_code == 404
