"""
Project registration and repository evidence inspection endpoints for CareerCrew.
Enables local project registration, safe repository scanning, evidence querying,
and skill verification against genuine software artifacts.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db.session import get_db
from app.core.logging import logger
from app.models import Project, EvidenceRecord
from app.schemas.evidence import (
    ProjectRegisterRequest,
    ProjectResponse,
    EvidenceItem,
    SkillVerificationResult,
    EvidenceAssessment,
)
from app.services.evidence_service import evidence_service
from app.services.path_validator import PathValidationError

router = APIRouter()


@router.post("/projects/register", response_model=ProjectResponse, tags=["Project Intelligence"])
async def register_project(
    payload: ProjectRegisterRequest,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Register a local user software repository for evidence scanning.
    Validates filesystem security constraints, extracts Git metadata, and indexes technical evidence.
    """
    try:
        project = evidence_service.register_project(
            name=payload.name,
            repo_path=payload.path,
            description=payload.description or "",
            db=db,
        )
        return evidence_service.get_project_summary(project.id, db)
    except PathValidationError as e:
        logger.warning(f"Project registration path validation rejected: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering project '{payload.name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to register project: {str(e)}")


@router.get("/projects", response_model=List[ProjectResponse], tags=["Project Intelligence"])
async def list_projects(db: Session = Depends(get_db)) -> List[ProjectResponse]:
    """Retrieve all registered software projects with scan metadata."""
    projects = db.scalars(select(Project).order_by(desc(Project.created_at))).all()
    results = []
    for p in projects:
        summary = evidence_service.get_project_summary(p.id, db)
        if summary:
            results.append(summary)
    return results


@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Project Intelligence"])
async def get_project(project_id: str, db: Session = Depends(get_db)) -> ProjectResponse:
    """Retrieve details and detected technologies for a specific registered project."""
    summary = evidence_service.get_project_summary(project_id, db)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return summary


@router.post("/projects/{project_id}/scan", response_model=ProjectResponse, tags=["Project Intelligence"])
async def scan_project_endpoint(
    project_id: str,
    force: bool = Query(default=True, description="Force re-scan regardless of commit hash cache"),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Trigger safe filesystem and git evidence scanning on a registered project.
    """
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    try:
        evidence_service.scan_project(project, db, force=force)
        summary = evidence_service.get_project_summary(project_id, db)
        if not summary:
            raise HTTPException(status_code=500, detail="Failed to retrieve project summary after scan")
        return summary
    except Exception as e:
        logger.error(f"Failed to scan project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan error: {str(e)}")


@router.get("/projects/{project_id}/evidence", response_model=List[EvidenceItem], tags=["Project Intelligence"])
async def get_project_evidence(
    project_id: str,
    technology: Optional[str] = Query(None, description="Filter by technology or skill"),
    db: Session = Depends(get_db),
) -> List[EvidenceItem]:
    """Retrieve atomic evidence records indexed from a project's repository."""
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    stmt = select(EvidenceRecord).where(EvidenceRecord.project_id == project_id)
    if technology:
        stmt = stmt.where(
            (EvidenceRecord.technology.ilike(f"%{technology}%")) |
            (EvidenceRecord.canonical_skill.ilike(f"%{technology}%"))
        )
    records = db.scalars(stmt.order_by(desc(EvidenceRecord.confidence))).all()

    return [
        EvidenceItem(
            id=r.id,
            project_id=r.project_id,
            project_name=project.name,
            technology=r.technology,
            canonical_skill=r.canonical_skill,
            evidence_type=r.evidence_type,
            source_file=r.source_file,
            source_location=r.source_location,
            description=r.description,
            confidence=r.confidence,
            confidence_level=r.confidence_level,
            detector=r.detector,
            snippet=r.snippet,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in records
    ]


@router.post("/projects/verify-skills", response_model=List[SkillVerificationResult], tags=["Project Intelligence"])
async def verify_skills_endpoint(
    payload: Dict[str, List[str]] = Body(..., example={"skills": ["Python", "FastAPI", "PostgreSQL", "Kubernetes"]}),
    db: Session = Depends(get_db),
) -> List[SkillVerificationResult]:
    """
    Evaluate candidate skills against registered local repositories and return
    confidence classifications: VERIFIED, LIKELY, WEAK, or UNVERIFIED.
    """
    skills = payload.get("skills", [])
    if not skills:
        return []

    results = []
    for s in skills:
        if s and s.strip():
            results.append(evidence_service.verify_skill(s.strip(), db))
    return results
