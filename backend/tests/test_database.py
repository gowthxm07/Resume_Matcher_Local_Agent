"""
Unit tests for database initialization, schema integrity, and model persistence.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.init_db import init_db, check_db_health
from app.models import Resume, JobDescription, Project, Application, AnalysisRun


def test_database_health_check(db_session: Session):
    """Verify that all core tables are recognized by the schema inspector."""
    engine = db_session.bind
    init_db(engine)
    health = check_db_health(engine)
    assert health["connected"] is True
    assert health["engine"] == "sqlite"
    assert "resumes" in health["tables"]
    assert "job_descriptions" in health["tables"]
    assert "projects" in health["tables"]
    assert "applications" in health["tables"]
    assert "analysis_runs" in health["tables"]


def test_resume_model_crud(db_session: Session):
    """Verify Resume model can be created, saved, and queried."""
    resume = Resume(
        filename="john_doe_resume.pdf",
        file_path="/data/resumes/john_doe_resume.pdf",
        file_type="pdf",
        file_size_bytes=10240,
        raw_text="Experienced Software Engineer with Python and React skills.",
        status="uploaded",
        parsed_metadata={"author": "John Doe", "pages": 1},
    )
    db_session.add(resume)
    db_session.commit()

    saved = db_session.scalar(select(Resume).where(Resume.filename == "john_doe_resume.pdf"))
    assert saved is not None
    assert saved.id is not None
    assert saved.file_type == "pdf"
    assert "Software Engineer" in saved.raw_text
    assert saved.parsed_metadata["author"] == "John Doe"


def test_job_description_model_crud(db_session: Session):
    """Verify JobDescription model can be created and queried."""
    jd = JobDescription(
        title="Senior Python Backend Developer",
        company="Acme Robotics",
        raw_text="Must have 5+ years experience in Python, FastAPI, and local LLM systems.",
        status="pending",
    )
    db_session.add(jd)
    db_session.commit()

    saved = db_session.scalar(select(JobDescription).where(JobDescription.title == "Senior Python Backend Developer"))
    assert saved is not None
    assert saved.company == "Acme Robotics"


def test_application_and_analysis_relationship(db_session: Session):
    """Verify Application and AnalysisRun relationship linking resume and job description."""
    resume = Resume(
        filename="dev.pdf",
        file_path="/data/resumes/dev.pdf",
        file_type="pdf",
        raw_text="Python Engineer",
    )
    jd = JobDescription(
        title="ML Ops Engineer",
        company="Local AI Corp",
        raw_text="ML Engineer needed",
    )
    db_session.add_all([resume, jd])
    db_session.commit()

    app = Application(
        resume_id=resume.id,
        job_description_id=jd.id,
        target_role="ML Ops Engineer",
        company_name="Local AI Corp",
        status="draft",
    )
    db_session.add(app)
    db_session.commit()

    run = AnalysisRun(
        resume_id=resume.id,
        job_description_id=jd.id,
        application_id=app.id,
        run_type="initial_assessment",
        status="completed",
        match_score=85.5,
    )
    db_session.add(run)
    db_session.commit()

    saved_run = db_session.scalar(select(AnalysisRun).where(AnalysisRun.id == run.id))
    assert saved_run is not None
    assert saved_run.match_score == 85.5
    assert saved_run.application.target_role == "ML Ops Engineer"
