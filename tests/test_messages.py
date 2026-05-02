"""Tests for message API endpoints."""

import json


def _create_project(client):
    """Helper to create a project and return its ID."""
    res = client.post("/api/projects",
        data=json.dumps({"name": "Chat Test Project"}),
        content_type="application/json")
    return res.get_json()["data"]["id"]


def test_send_message(client):
    """Test sending a message to a project chat."""
    pid = _create_project(client)
    response = client.post(f"/api/projects/{pid}/messages",
        data=json.dumps({"content": "Hello team!", "sender": "Alice"}),
        content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["content"] == "Hello team!"
    assert data["sender"] == "Alice"


def test_send_message_empty_content(client):
    """Test that empty message content is rejected."""
    pid = _create_project(client)
    response = client.post(f"/api/projects/{pid}/messages",
        data=json.dumps({"content": "", "sender": "Bob"}),
        content_type="application/json")
    assert response.status_code == 400


def test_send_message_nonexistent_project(client):
    """Test sending message to nonexistent project returns 404."""
    response = client.post("/api/projects/fake_id/messages",
        data=json.dumps({"content": "Hello", "sender": "Eve"}),
        content_type="application/json")
    assert response.status_code == 404


def test_list_messages(client):
    """Test listing messages for a project."""
    pid = _create_project(client)
    client.post(f"/api/projects/{pid}/messages",
        data=json.dumps({"content": "Msg 1", "sender": "Alice"}),
        content_type="application/json")
    client.post(f"/api/projects/{pid}/messages",
        data=json.dumps({"content": "Msg 2", "sender": "Bob"}),
        content_type="application/json")
    response = client.get(f"/api/projects/{pid}/messages")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data) == 2


def test_list_messages_nonexistent_project(client):
    """Test listing messages for nonexistent project returns 404."""
    response = client.get("/api/projects/fake_id/messages")
    assert response.status_code == 404
