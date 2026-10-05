"""
Integration tests for the Match Analysis API endpoints.
Verifies document ingestion, match calculation, SQLite persistence, and error handling.
"""

from fastapi.testclient import TestClient


def test_analysis_match_with_direct_text(client: TestClient):
    """Verify POST /api/analysis/match with raw text inputs."""
    resume_text = """John Developer
john@example.com
Summary: Backend engineer with Python, FastAPI, and PostgreSQL experience.
Skills: Python, FastAPI, PostgreSQL, Git, Docker
Experience:
Senior Engineer at Tech Corp (3 years). Built APIs in FastAPI and managed PostgreSQL databases.
Projects:
API Gateway: Microservice gateway in Python with PostgreSQL storage."""

    jd_text = """Python Backend Engineer
Requirements:
- Python
- FastAPI
- PostgreSQL
Preferred:
- Docker"""

    response = client.post(
        "/api/analysis/match",
        data={
            "resume_text": resume_text,
            "jd_text": jd_text,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert data["overall_score"] >= 70.0
    assert "dimension_scores" in data
    assert "requirements_analysis" in data
    assert data["analysis_run_id"] is not None

    # Verify retrieval of saved analysis
    run_id = data["analysis_run_id"]
    get_res = client.get(f"/api/analysis/{run_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["overall_score"] == data["overall_score"]


def test_analysis_match_missing_inputs(client: TestClient):
    """Verify POST /api/analysis/match returns 400 when missing inputs."""
    response = client.post("/api/analysis/match", data={})
    assert response.status_code == 400


def test_analysis_match_recent_history(client: TestClient):
    """Verify GET /api/analysis/history/recent returns saved runs."""
    res = client.get("/api/analysis/history/recent")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_nonexistent_analysis_404(client: TestClient):
    """Verify GET /api/analysis/nonexistent returns 404."""
    res = client.get("/api/analysis/nonexistent_id_12345")
    assert res.status_code == 404
