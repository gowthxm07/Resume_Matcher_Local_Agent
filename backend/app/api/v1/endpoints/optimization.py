"""
Resume optimization and version audit API endpoints for CareerCrew.
Enables evidence-grounded iterative rewriting, claim fact checking, ATS validation,
and querying persistent resume versions and audit trails.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.resume import Resume
from app.models.analysis_run import AnalysisRun
from app.models.resume_version import ResumeVersion
from app.schemas.optimization import (
    OptimizeRequest,
    OptimizeResponse,
    OptimizationDossier,
    ResumeVersionSchema,
)
from app.services.optimization_service import optimization_service
from app.core.logging import logger

router = APIRouter()


@router.post("/analysis/optimize", response_model=OptimizeResponse, tags=["Resume Optimization"])
async def optimize_resume(
    payload: OptimizeRequest,
    db: Session = Depends(get_db),
) -> OptimizeResponse:
    """
    Execute evidence-grounded multi-agent resume optimization.
    Iteratively enhances bullet points and keyword alignment, fact-checks every modification,
    validates ATS compatibility, and records immutable resume versions.
    """
    try:
        response = optimization_service.run_optimization(
            resume_id=payload.resume_id,
            job_description_id=payload.job_description_id,
            project_ids=payload.project_ids,
            raw_resume_text=payload.raw_resume_text,
            raw_jd_text=payload.raw_jd_text,
            max_iterations=payload.max_iterations,
            db=db,
            use_live_llm=payload.use_live_llm,
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.error(f"Error during resume optimization: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(exc)}")


@router.get("/resumes/{id}/versions", response_model=List[ResumeVersionSchema], tags=["Resume Versioning"])
async def get_resume_versions(
    id: str,
    db: Session = Depends(get_db),
) -> List[ResumeVersionSchema]:
    """
    Retrieve all immutable optimization versions and iteration snapshots for a given resume ID.
    """
    resume = db.scalar(select(Resume).where(Resume.id == id))
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume with ID '{id}' not found.")

    versions = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == id)
        .order_by(ResumeVersion.iteration.asc())
        .all()
    )

    return [
        ResumeVersionSchema(
            id=v.id,
            resume_id=v.resume_id,
            parent_version_id=v.parent_version_id,
            analysis_id=v.analysis_id,
            iteration=v.iteration,
            content=v.content,
            match_score=v.match_score,
            ats_score=v.ats_score,
            evidence_confidence=v.evidence_confidence,
            status=v.status,
            change_summary=v.change_summary or {},
            audit_trail=v.audit_trail or [],
            created_at=v.created_at.isoformat() if v.created_at else "",
        )
        for v in versions
    ]


@router.get("/resumes/{id}/versions/{version_id}", response_model=ResumeVersionSchema, tags=["Resume Versioning"])
async def get_resume_version_detail(
    id: str,
    version_id: str,
    db: Session = Depends(get_db),
) -> ResumeVersionSchema:
    """
    Retrieve details of a specific resume version snapshot by version ID.
    """
    version = db.scalar(
        select(ResumeVersion).where(
            ResumeVersion.id == version_id,
            ResumeVersion.resume_id == id,
        )
    )
    if not version:
        raise HTTPException(
            status_code=404,
            detail=f"Version '{version_id}' for resume '{id}' not found.",
        )

    return ResumeVersionSchema(
        id=version.id,
        resume_id=version.resume_id,
        parent_version_id=version.parent_version_id,
        analysis_id=version.analysis_id,
        iteration=version.iteration,
        content=version.content,
        match_score=version.match_score,
        ats_score=version.ats_score,
        evidence_confidence=version.evidence_confidence,
        status=version.status,
        change_summary=version.change_summary or {},
        audit_trail=version.audit_trail or [],
        created_at=version.created_at.isoformat() if version.created_at else "",
    )


@router.get("/analysis/{analysis_id}/optimization", tags=["Resume Optimization"])
async def get_optimization_result(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retrieve stored optimization results and version summary for an analysis run.
    """
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found.")

    versions = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.analysis_id == analysis_id)
        .order_by(ResumeVersion.iteration.asc())
        .all()
    )

    return {
        "analysis_id": run.id,
        "resume_id": run.resume_id,
        "job_description_id": run.job_description_id,
        "execution_mode": run.execution_mode,
        "match_score": run.match_score,
        "evidence_confidence": run.evidence_confidence,
        "results_summary": run.results_summary or {},
        "versions_count": len(versions),
        "versions": [
            {
                "id": v.id,
                "iteration": v.iteration,
                "status": v.status,
                "match_score": v.match_score,
                "ats_score": v.ats_score,
                "created_at": v.created_at.isoformat() if v.created_at else "",
            }
            for v in versions
        ],
    }


@router.get("/analysis/{analysis_id}/audit", tags=["Resume Optimization"])
async def get_optimization_audit(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retrieve comprehensive audit trail of all proposed modifications, claim evaluations,
    and fact-checker decisions for an analysis run.
    """
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found.")

    versions = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.analysis_id == analysis_id)
        .order_by(ResumeVersion.iteration.asc())
        .all()
    )

    all_audit_trails = []
    for v in versions:
        if v.audit_trail:
            for item in v.audit_trail:
                all_audit_trails.append({
                    "version_id": v.id,
                    "iteration": v.iteration,
                    **item,
                })

    return {
        "analysis_id": run.id,
        "audit_trail": all_audit_trails,
        "total_audited_changes": len(all_audit_trails),
    }
