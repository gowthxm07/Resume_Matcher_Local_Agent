"""
Database introspection endpoints for CareerCrew.
Provides local dataset counts and table statistics.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.models import Resume, JobDescription, Project, Application, AnalysisRun

router = APIRouter()


@router.get("/database/summary", tags=["Persistent Storage"])
async def get_database_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve counts of saved entities across all persistent tables."""
    resume_count = db.scalar(select(func.count()).select_from(Resume)) or 0
    jd_count = db.scalar(select(func.count()).select_from(JobDescription)) or 0
    project_count = db.scalar(select(func.count()).select_from(Project)) or 0
    app_count = db.scalar(select(func.count()).select_from(Application)) or 0
    run_count = db.scalar(select(func.count()).select_from(AnalysisRun)) or 0

    return {
        "status": "connected",
        "engine": "sqlite",
        "counts": {
            "resumes": resume_count,
            "job_descriptions": jd_count,
            "projects": project_count,
            "applications": app_count,
            "analysis_runs": run_count,
        },
    }
