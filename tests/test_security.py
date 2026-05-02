"""Security tests for TeamFlow."""


def test_security_headers(client):
    """Test that security headers are present on responses."""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Content-Security-Policy" in response.headers


def test_invalid_content_type(client):
    """Test that POST without JSON content-type is rejected."""
    response = client.post("/api/projects",
        data="not json",
        content_type="text/plain")
    assert response.status_code == 415


def test_xss_prevention(client):
    """Test that HTML in input is sanitized."""
    import json
    response = client.post("/api/projects",
        data=json.dumps({"name": "<script>alert('xss')</script>Test"}),
        content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert "<script>" not in data["name"]
    assert "alert" not in data["name"]
