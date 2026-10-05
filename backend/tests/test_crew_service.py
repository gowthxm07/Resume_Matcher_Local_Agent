"""
Tests for CrewExecutionService orchestration, error handling, telemetry, and benchmark generation.
"""

from pathlib import Path
import pytest
from app.services.crew_service import crew_service
from app.services.evidence_service import evidence_service
from app.schemas.dossier import FinalAnalysisDossier, BenchmarkComparisonResult

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "repos"


SAMPLE_RESUME_TEXT = """
Alex Chen
alex.chen@example.com | San Francisco, CA

Professional Summary:
Senior Python Backend Engineer with 5+ years of experience designing microservices using FastAPI, PostgreSQL, and Docker.

Skills:
- Languages: Python, JavaScript, SQL
- Frameworks: FastAPI, SQLAlchemy, Pydantic, PyTest
- Databases: PostgreSQL, Redis
- Infrastructure: Docker, Git

Experience:
Senior Software Engineer | TechCorp | 2021 - Present
- Architected high-throughput microservices using FastAPI and PostgreSQL handling 10k req/sec.
- Indexed database tables and reduced query latency by 40%.
- Containerized applications using Docker.

Education:
B.S. in Computer Science | UC Berkeley | 2018
"""

SAMPLE_JD_TEXT = """
Senior Python Developer
Company: DataWave
Location: Remote

Requirements:
- 5+ years of software engineering experience in Python.
- Strong proficiency in FastAPI or Flask.
- Experience with relational databases (PostgreSQL preferred).
- Docker and containerization experience.

Preferred:
- Redis caching.
- Automated testing with PyTest.
"""


def test_crew_service_valid_analysis_with_raw_text(db_session):
    """Verify CrewExecutionService produces valid FinalAnalysisDossier from text inputs."""
    dossier = crew_service.run_analysis(
        raw_resume_text=SAMPLE_RESUME_TEXT,
        raw_jd_text=SAMPLE_JD_TEXT,
        db=db_session,
        use_live_llm=False,
    )

    assert isinstance(dossier, FinalAnalysisDossier)
    assert dossier.overall_match_score > 70.0
    assert dossier.classification in ["STRONG_FIT", "POTENTIAL_FIT"]
    assert len(dossier.critical_requirements) > 0
    assert len(dossier.strong_matches) > 0
    assert "Python" in dossier.strong_matches or any("Python" in m for m in dossier.strong_matches)
    assert len(dossier.key_strengths) > 0

    # Verify telemetry presence
    summary = dossier.agent_execution_summary
    assert summary is not None
    assert summary["execution_mode"] == "crew_multi_agent"
    assert len(summary["agents_active"]) == 5
    assert len(summary["agents_inactive"]) == 4
    assert len(summary["telemetry"]) == 5

    # Verify timing breakdown
    timing = dossier.timing_information
    assert "total_ms" in timing
    assert "manager_agent_ms" in timing


def test_crew_service_missing_resume_raises(db_session):
    """Verify ValueError is raised when resume ID does not exist."""
    with pytest.raises(ValueError) as exc:
        crew_service.run_analysis(
            resume_id="non-existent-resume-id",
            raw_jd_text=SAMPLE_JD_TEXT,
            db=db_session,
            use_live_llm=False,
        )
    assert "not found" in str(exc.value)


def test_crew_service_missing_jd_raises(db_session):
    """Verify ValueError is raised when JD ID does not exist."""
    with pytest.raises(ValueError) as exc:
        crew_service.run_analysis(
            raw_resume_text=SAMPLE_RESUME_TEXT,
            job_description_id="non-existent-jd-id",
            db=db_session,
            use_live_llm=False,
        )
    assert "not found" in str(exc.value)


def test_crew_service_empty_text_raises(db_session):
    """Verify ValueError is raised when empty text is passed."""
    with pytest.raises(ValueError):
        crew_service.run_analysis(
            raw_resume_text="",
            raw_jd_text=SAMPLE_JD_TEXT,
            db=db_session,
            use_live_llm=False,
        )


def test_crew_service_with_registered_project(db_session):
    """Verify CrewExecutionService grounds verified skills when candidate repository is registered."""
    repo_path = str(FIXTURES_DIR / "python_fastapi_backend")
    project = evidence_service.register_project(
        name="FastAPI Backend",
        repo_path=repo_path,
        description="Core FastAPI service",
        db=db_session,
    )
    evidence_service.scan_project(project.id, db_session)

    dossier = crew_service.run_analysis(
        raw_resume_text=SAMPLE_RESUME_TEXT,
        raw_jd_text=SAMPLE_JD_TEXT,
        project_ids=[project.id],
        db=db_session,
        use_live_llm=False,
    )

    assert dossier.evidence_confidence_score > 0.0
    assert len(dossier.verified_skills) > 0
    # FastAPI or Python should be verified in repo
    verified_lower = [s.lower() for s in dossier.verified_skills]
    assert "fastapi" in verified_lower or "python" in verified_lower
    assert len(dossier.project_evidence) > 0


def test_crew_service_benchmark_comparison(db_session):
    """Verify CrewExecutionService produces side-by-side benchmark contrasting baseline vs crew."""
    bm = crew_service.run_benchmark(
        raw_resume_text=SAMPLE_RESUME_TEXT,
        raw_jd_text=SAMPLE_JD_TEXT,
        db=db_session,
    )

    assert isinstance(bm, BenchmarkComparisonResult)
    assert bm.baseline_match_score > 0
    assert bm.crew_match_score > 0
    assert bm.baseline_execution_ms > 0
    assert len(bm.synthesis_insights) > 0
