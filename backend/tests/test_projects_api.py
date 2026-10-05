"""
API integration tests for Project & Evidence endpoints.
Verifies registration, scanning, querying, and skill verification endpoints.
"""

from pathlib import Path
from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "repos"


def test_register_project_api_success(client: TestClient):
    """Verify POST /api/projects/register registers a repository and indexes technologies."""
    payload = {
        "name": "FastAPI API Service",
        "path": str(FIXTURES_DIR / "python_fastapi_backend"),
        "description": "Integration test project",
    }
    response = client.post("/api/projects/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FastAPI API Service"
    assert data["evidence_count"] > 0
    assert "FastAPI" in data["detected_technologies"]


def test_register_project_api_security_rejection(client: TestClient):
    """Verify POST /api/projects/register rejects unsafe system paths."""
    payload = {
        "name": "Malicious Path Attempt",
        "path": "C:\\Windows\\System32",
        "description": "Should fail",
    }
    response = client.post("/api/projects/register", json=payload)
    assert response.status_code == 400
    assert "denied" in response.json()["detail"].lower() or "prohibited" in response.json()["detail"].lower()


def test_list_and_get_projects_api(client: TestClient):
    """Verify GET /api/projects and GET /api/projects/{id}."""
    # Register project first
    payload = {
        "name": "Next.js Frontend App",
        "path": str(FIXTURES_DIR / "react_nextjs_app"),
        "description": "Frontend UI",
    }
    reg_res = client.post("/api/projects/register", json=payload)
    assert reg_res.status_code == 200
    proj_id = reg_res.json()["id"]

    # List projects
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(p["id"] == proj_id for p in items)

    # Get by ID
    get_res = client.get(f"/api/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proj_id
    assert "React" in get_res.json()["detected_technologies"]


def test_get_project_evidence_api(client: TestClient):
    """Verify GET /api/projects/{id}/evidence returns atomic evidence items."""
    reg_payload = {
        "name": "Postgres Docker Infra",
        "path": str(FIXTURES_DIR / "postgres_docker"),
    }
    reg_res = client.post("/api/projects/register", json=reg_payload)
    proj_id = reg_res.json()["id"]

    evidence_res = client.get(f"/api/projects/{proj_id}/evidence")
    assert evidence_res.status_code == 200
    evidence = evidence_res.json()
    assert len(evidence) > 0
    assert any(e["canonical_skill"].lower() == "postgresql" for e in evidence)


def test_verify_skills_api(client: TestClient):
    """Verify POST /api/projects/verify-skills evaluates multiple skills."""
    # Ensure a repo with FastAPI is registered
    client.post("/api/projects/register", json={
        "name": "FastAPI Backend",
        "path": str(FIXTURES_DIR / "python_fastapi_backend"),
    })

    verify_res = client.post("/api/projects/verify-skills", json={
        "skills": ["FastAPI", "PostgreSQL", "NonExistentTechnologyXYZ"]
    })
    assert verify_res.status_code == 200
    results = verify_res.json()
    assert len(results) == 3

    fastapi_item = next(r for r in results if r["canonical_skill"].lower() == "fastapi")
    assert fastapi_item["status"] == "VERIFIED"


    xyz_item = next(r for r in results if "xyz" in r["canonical_skill"].lower() or "nonexistent" in r["canonical_skill"].lower())
    assert xyz_item["status"] == "UNVERIFIED"
