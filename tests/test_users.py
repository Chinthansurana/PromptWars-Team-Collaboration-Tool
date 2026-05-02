"""Tests for user API endpoints."""

import json


def test_create_user(client):
    """Test creating a new user."""
    response = client.post("/api/users",
        data=json.dumps({"name": "Alice Johnson", "email": "alice@example.com", "role": "member"}),
        content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["name"] == "Alice Johnson"
    assert data["data"]["email"] == "alice@example.com"
    assert "id" in data["data"]


def test_create_user_missing_name(client):
    """Test creating user without name returns 400."""
    response = client.post("/api/users",
        data=json.dumps({"email": "test@example.com"}),
        content_type="application/json")
    assert response.status_code == 400


def test_create_user_missing_email(client):
    """Test creating user without email returns 400."""
    response = client.post("/api/users",
        data=json.dumps({"name": "Test User"}),
        content_type="application/json")
    assert response.status_code == 400


def test_create_user_invalid_email(client):
    """Test creating user with invalid email returns 400."""
    response = client.post("/api/users",
        data=json.dumps({"name": "Test User", "email": "invalid-email"}),
        content_type="application/json")
    assert response.status_code == 400


def test_create_user_invalid_role(client):
    """Test creating user with invalid role returns 400."""
    response = client.post("/api/users",
        data=json.dumps({"name": "Test User", "email": "test@example.com", "role": "invalid"}),
        content_type="application/json")
    assert response.status_code == 400


def test_create_user_duplicate_email(client):
    """Test creating user with duplicate email returns 409."""
    # Create first user
    client.post("/api/users",
        data=json.dumps({"name": "Alice", "email": "alice@example.com"}),
        content_type="application/json")
    # Try to create second user with same email
    response = client.post("/api/users",
        data=json.dumps({"name": "Bob", "email": "alice@example.com"}),
        content_type="application/json")
    assert response.status_code == 409


def test_list_users(client):
    """Test listing users."""
    client.post("/api/users",
        data=json.dumps({"name": "Alice", "email": "alice@example.com"}),
        content_type="application/json")
    client.post("/api/users",
        data=json.dumps({"name": "Bob", "email": "bob@example.com"}),
        content_type="application/json")
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 2


def test_get_user_not_found(client):
    """Test getting a non-existent user returns 404."""
    response = client.get("/api/users/nonexistent")
    assert response.status_code == 404


def test_update_user(client):
    """Test updating a user."""
    # Create user
    create_response = client.post("/api/users",
        data=json.dumps({"name": "Alice", "email": "alice@example.com"}),
        content_type="application/json")
    user_id = create_response.get_json()["data"]["id"]
    
    # Update user
    response = client.put(f"/api/users/{user_id}",
        data=json.dumps({"name": "Alice Smith", "role": "editor"}),
        content_type="application/json")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "Alice Smith"
    assert data["data"]["role"] == "editor"


def test_update_user_not_found(client):
    """Test updating a non-existent user returns 404."""
    response = client.put("/api/users/nonexistent",
        data=json.dumps({"name": "Updated"}),
        content_type="application/json")
    assert response.status_code == 404


def test_delete_user(client):
    """Test deleting a user."""
    # Create user
    create_response = client.post("/api/users",
        data=json.dumps({"name": "Alice", "email": "alice@example.com"}),
        content_type="application/json")
    user_id = create_response.get_json()["data"]["id"]
    
    # Delete user
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 200
    
    # Verify deletion
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404


def test_delete_user_not_found(client):
    """Test deleting a non-existent user returns 404."""
    response = client.delete("/api/users/nonexistent")
    assert response.status_code == 404
