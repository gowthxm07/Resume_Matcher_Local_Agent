"""
Integration tests for FastAPI endpoints:
POST /api/analysis/optimize
GET /api/resumes/{id}/versions
GET /api/resumes/{id}/versions/{version_id}
GET /api/analysis/{analysis_id}/optimization
GET /api/analysis/{analysis_id}/audit
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.project import Project


def test_api_optimize_endpoint(client, db_session: Session):
    """Verify POST /api/analysis/optimize executes optimization and returns structured response."""
    resume = Resume(
        filename="api_candidate.txt",
        file_path="direct://text",
        file_type="txt",
        raw_text="EXPERIENCE\nDeveloper\n- Built an AI receptionist.\n",
        status="extracted",
    )
    jd = JobDescription(
        title="AI Engineer",
        raw_text="Requires Next.js, Express, PostgreSQL, and Ollama.",
    )
    project = Project(
        name="AI Receptionist",
        repo_path="/mock/repo",
        evidence_metadata={"technologies": ["next.js", "express", "postgresql", "ollama"]},
    )
    db_session.add_all([resume, jd, project])
    db_session.commit()

    from app.models.evidence_record import EvidenceRecord
    for tech in ["next.js", "express", "postgresql", "ollama"]:
        rec = EvidenceRecord(
            project_id=project.id,
            technology=tech,
            canonical_skill=tech.title(),
            evidence_type="dependency",
            source_file="package.json",
            description=f"Verified dependency for {tech}",
            confidence=0.95,
            confidence_level="VERIFIED",
        )
        db_session.add(rec)
    db_session.commit()

    payload = {
        "resume_id": resume.id,
        "job_description_id": jd.id,
        "project_ids": [project.id],
        "max_iterations": 2,
    }

    res = client.post("/api/analysis/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "run_id" in data
    assert "dossier" in data
    assert "final_version" in data
    assert "versions" in data

    dossier = data["dossier"]
    assert dossier["baseline_match_score"] >= 0
    assert dossier["final_match_score"] >= 0
    assert "disclaimer" in dossier

    # Test GET /api/resumes/{id}/versions
    v_res = client.get(f"/api/resumes/{resume.id}/versions")
    assert v_res.status_code == 200
    v_data = v_res.json()
    assert len(v_data) >= 1

    first_ver = v_data[0]
    ver_id = first_ver["id"]

    # Test GET /api/resumes/{id}/versions/{version_id}
    detail_res = client.get(f"/api/resumes/{resume.id}/versions/{ver_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == ver_id

    # Test GET /api/analysis/{analysis_id}/optimization
    run_id = data["run_id"]
    opt_res = client.get(f"/api/analysis/{run_id}/optimization")
    assert opt_res.status_code == 200
    assert opt_res.json()["analysis_id"] == run_id

    # Test GET /api/analysis/{analysis_id}/audit
    audit_res = client.get(f"/api/analysis/{run_id}/audit")
    assert audit_res.status_code == 200
    assert "audit_trail" in audit_res.json()


def test_api_optimize_invalid_resume(client):
    """Verify optimization fails with 400 when no resume is found or provided."""
    res = client.post("/api/analysis/optimize", json={"resume_id": "non_existent_id"})
    assert res.status_code == 400


def test_api_get_versions_404(client):
    """Verify 404 for unknown resume ID."""
    res = client.get("/api/resumes/unknown_id/versions")
    assert res.status_code == 404
