"""
Unit tests for FastAPI health and system introspection endpoints.
"""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Verify GET /api/health returns 200 with service information."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "careercrew-backend"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client: TestClient):
    """Verify GET / returns basic service discovery payload."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "privacy-first-local"
    assert data["health"] == "/api/health"


def test_system_status_endpoint(client: TestClient):
    """Verify GET /api/system/status returns structured system diagnostics."""
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend_status" in data
    assert data["local_only_verified"] is True
    assert "ollama" in data
    assert "database" in data
    assert "vector_store" in data

    # Check Ollama status structure
    ollama = data["ollama"]
    assert "reachable" in ollama
    assert "configured_model" in ollama
    assert ollama["configured_model"] == "llama3.2:3b"

    # Check Database status structure
    db = data["database"]
    assert db["engine"] == "sqlite"
    assert "connected" in db

    # Check Vector store status structure
    vs = data["vector_store"]
    assert vs["store_type"] == "chroma"
