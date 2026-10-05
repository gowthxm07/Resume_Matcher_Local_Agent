"""
Tests for CrewAI multi-agent API endpoints:
- POST /api/analysis/crew
- GET /api/analysis/{id}/dossier
- POST /api/analysis/benchmark
"""

import pytest
from app.models.resume import Resume
from app.models.job_description import JobDescription


SAMPLE_RESUME = "Senior Python engineer with 6 years experience in FastAPI, Docker, and PostgreSQL."
SAMPLE_JD = "Looking for Senior Python developer with FastAPI and PostgreSQL expertise."


def test_crew_analysis_api_with_raw_text(client):
    """Test POST /api/analysis/crew with raw text inputs."""
    payload = {
        "raw_resume_text": SAMPLE_RESUME,
        "raw_jd_text": SAMPLE_JD,
        "use_live_llm": False,
    }
    response = client.post("/api/analysis/crew", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    assert "overall_match_score" in data
    assert "classification" in data
    assert "agent_execution_summary" in data
    assert data["agent_execution_summary"]["execution_mode"] == "crew_multi_agent"


def test_crew_analysis_api_invalid_payload(client):
    """Test POST /api/analysis/crew with empty payload fails with 400."""
    payload = {
        "raw_resume_text": "",
        "raw_jd_text": "",
        "use_live_llm": False,
    }
    response = client.post("/api/analysis/crew", json=payload)
    assert response.status_code == 400


def test_crew_analysis_api_with_db_entities(client, db_session):
    """Test POST /api/analysis/crew with database entity IDs and retrieval of dossier."""
    res_obj = Resume(
        filename="db_resume.txt",
        file_path="direct://text",
        file_type="txt",
        file_size_bytes=len(SAMPLE_RESUME),
        raw_text=SAMPLE_RESUME,
        status="extracted",
    )
    jd_obj = JobDescription(
        title="Python Engineer",
        company="TechCorp",
        raw_text=SAMPLE_JD,
        status="active",
    )
    db_session.add(res_obj)
    db_session.add(jd_obj)
    db_session.commit()
    db_session.refresh(res_obj)
    db_session.refresh(jd_obj)

    payload = {
        "resume_id": res_obj.id,
        "job_description_id": jd_obj.id,
        "use_live_llm": False,
    }
    response = client.post("/api/analysis/crew", json=payload)
    assert response.status_code == 200
    data = response.json()
    analysis_id = data["analysis_id"]

    # Verify retrieval via GET /api/analysis/{id}/dossier
    get_res = client.get(f"/api/analysis/{analysis_id}/dossier")
    assert get_res.status_code == 200
    dossier_data = get_res.json()
    assert dossier_data["analysis_id"] == analysis_id
    assert dossier_data["resume_id"] == res_obj.id


def test_get_dossier_not_found(client):
    """Test GET /api/analysis/{id}/dossier with invalid ID returns 404."""
    response = client.get("/api/analysis/invalid-dossier-id-999/dossier")
    assert response.status_code == 404


def test_benchmark_api_endpoint(client):
    """Test POST /api/analysis/benchmark produces side-by-side comparison metrics."""
    payload = {
        "raw_resume_text": SAMPLE_RESUME,
        "raw_jd_text": SAMPLE_JD,
    }
    response = client.post("/api/analysis/benchmark", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "baseline_match_score" in data
    assert "crew_match_score" in data
    assert "evidence_confidence_score" in data
    assert "baseline_execution_ms" in data
    assert "crew_execution_ms" in data
    assert "synthesis_insights" in data
    assert len(data["synthesis_insights"]) > 0
