"""
Match analysis API endpoints for CareerCrew.
Transforms resume and job description documents into structured profiles,
computes explainable multidimensional match scores, and persists analysis runs to SQLite.
"""

import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db.session import get_db
from app.core.logging import logger
from app.models import Resume, JobDescription, AnalysisRun
from app.ingestion.parser import DocumentParser, sanitize_filename
from app.services.extractor_service import extractor_service
from app.services.matching_engine import matching_engine
from app.schemas.intelligence import AnalysisResult
from app.schemas.evidence import EvidenceAssessment
from app.services.evidence_service import evidence_service



router = APIRouter()


@router.post("/analysis/match", response_model=AnalysisResult, tags=["Match Intelligence"])
async def analyze_match(
    resume_file: Optional[UploadFile] = File(None),
    jd_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: Optional[str] = Form(None),
    resume_id: Optional[str] = Form(None),
    job_description_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> AnalysisResult:
    """
    Execute baseline match analysis between a candidate resume and a job description.
    Accepts files, raw text, or database IDs.
    Calculates explainable scores across 7 dimensions and classifies all requirements.
    """
    total_start = time.perf_counter()
    extract_start = time.perf_counter()

    final_resume_text = ""
    final_jd_text = ""
    saved_resume = None
    saved_jd = None

    # 1. Resolve Resume Text
    if resume_file and resume_file.filename:
        content = await resume_file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded resume file is empty")
        safe_name = sanitize_filename(resume_file.filename)
        doc = DocumentParser.parse_bytes(content, safe_name)
        final_resume_text = doc.extracted_text

        # Persist resume record in database
        saved_resume = Resume(
            filename=safe_name,
            file_path=f"upload://{safe_name}",
            file_type=doc.document_type,
            file_size_bytes=len(content),
            raw_text=final_resume_text,
            status="extracted",
            parsed_metadata=doc.metadata,
        )
        db.add(saved_resume)
        db.commit()
        db.refresh(saved_resume)
        resume_id = saved_resume.id

    elif resume_id:
        saved_resume = db.scalar(select(Resume).where(Resume.id == resume_id))
        if not saved_resume:
            raise HTTPException(status_code=404, detail=f"Resume '{resume_id}' not found in database")
        final_resume_text = saved_resume.raw_text

    elif resume_text and resume_text.strip():
        final_resume_text = resume_text.strip()
        saved_resume = Resume(
            filename="direct_text_resume.txt",
            file_path="direct://text",
            file_type="txt",
            file_size_bytes=len(final_resume_text),
            raw_text=final_resume_text,
            status="extracted",
        )
        db.add(saved_resume)
        db.commit()
        db.refresh(saved_resume)
        resume_id = saved_resume.id
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either resume_file, resume_id, or resume_text",
        )

    # 2. Resolve Job Description Text
    if jd_file and jd_file.filename:
        content = await jd_file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded job description file is empty")
        safe_name = sanitize_filename(jd_file.filename)
        doc = DocumentParser.parse_bytes(content, safe_name)
        final_jd_text = doc.extracted_text

        saved_jd = JobDescription(
            title=safe_name.replace(".pdf", "").replace(".docx", "").replace(".txt", ""),
            company="Uploaded Company",
            raw_text=final_jd_text,
            status="extracted",
            parsed_metadata=doc.metadata,
        )
        db.add(saved_jd)
        db.commit()
        db.refresh(saved_jd)
        job_description_id = saved_jd.id

    elif job_description_id:
        saved_jd = db.scalar(select(JobDescription).where(JobDescription.id == job_description_id))
        if not saved_jd:
            raise HTTPException(
                status_code=404, detail=f"Job Description '{job_description_id}' not found"
            )
        final_jd_text = saved_jd.raw_text

    elif jd_text and jd_text.strip():
        final_jd_text = jd_text.strip()
        saved_jd = JobDescription(
            title="Direct Input Job Description",
            company="Company",
            raw_text=final_jd_text,
            status="extracted",
        )
        db.add(saved_jd)
        db.commit()
        db.refresh(saved_jd)
        job_description_id = saved_jd.id
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either jd_file, job_description_id, or jd_text",
        )

    extraction_time_ms = (time.perf_counter() - extract_start) * 1000.0

    # 3. Extract structured profiles
    llm_start = time.perf_counter()
    resume_profile = await extractor_service.extract_resume(final_resume_text)
    job_profile = await extractor_service.extract_job_description(final_jd_text)
    inference_time_ms = (time.perf_counter() - llm_start) * 1000.0

    # Update Job Description title / company if extracted from profile
    if saved_jd and job_profile.title != "Target Position":
        saved_jd.title = job_profile.title
        saved_jd.company = job_profile.company
        db.commit()

    # 4. Compute Match Assessment
    analysis_res = await matching_engine.analyze_match(
        resume=resume_profile,
        job=job_profile,
        resume_id=resume_id,
        job_description_id=job_description_id,
    )

    total_time_ms = (time.perf_counter() - total_start) * 1000.0

    # Update metadata
    analysis_res.metadata.extraction_time_ms = round(extraction_time_ms, 2)
    analysis_res.metadata.inference_time_ms = round(inference_time_ms, 2)
    analysis_res.metadata.total_time_ms = round(total_time_ms, 2)

    # 5. Persist AnalysisRun to SQLite
    analysis_run = AnalysisRun(
        resume_id=resume_id,
        job_description_id=job_description_id,
        run_type="baseline_match",
        status="completed",
        match_score=analysis_res.overall_score,
        results_summary=analysis_res.model_dump(),
        error_message=None,
    )
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)

    analysis_res.analysis_run_id = analysis_run.id
    return analysis_res


@router.get("/analysis/{analysis_id}", response_model=AnalysisResult, tags=["Match Intelligence"])
async def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)) -> AnalysisResult:
    """Retrieve a completed analysis run from local persistent storage."""
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found")
    if not run.results_summary:
        raise HTTPException(status_code=404, detail="Analysis results summary is empty")
    return AnalysisResult(**run.results_summary)


@router.get("/analysis/history/recent", tags=["Match Intelligence"])
async def list_recent_analyses(limit: int = 10, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """List recent analysis runs with high-level summary metrics."""
    runs = db.scalars(
        select(AnalysisRun).order_by(desc(AnalysisRun.started_at)).limit(limit)
    ).all()

    items = []
    for r in runs:
        items.append({
            "id": r.id,
            "resume_id": r.resume_id,
            "job_description_id": r.job_description_id,
            "status": r.status,
            "match_score": r.match_score,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "summary": r.results_summary.get("summary_explanation", "") if r.results_summary else "",
        })
    return items


@router.get("/analysis/{analysis_id}/evidence", response_model=EvidenceAssessment, tags=["Match Intelligence"])
async def get_analysis_evidence(analysis_id: str, db: Session = Depends(get_db)) -> EvidenceAssessment:
    """
    Generate or retrieve evidence-grounded verification linking:
    Job Requirement -> Resume Claim -> Candidate Project -> Repository Evidence.
    Computes an independent Evidence Confidence Score.
    """
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found")
    if not run.results_summary:
        raise HTTPException(status_code=404, detail="Analysis results summary is empty")

    analysis_res = AnalysisResult(**run.results_summary)
    resume_profile = None
    job_profile = None

    # Retrieve profiles from resume and JD if available
    if run.resume_id:
        resume_record = db.scalar(select(Resume).where(Resume.id == run.resume_id))
        if resume_record and resume_record.raw_text:
            resume_profile = await extractor_service.extract_resume(resume_record.raw_text)

    if run.job_description_id:
        jd_record = db.scalar(select(JobDescription).where(JobDescription.id == run.job_description_id))
        if jd_record and jd_record.raw_text:
            job_profile = await extractor_service.extract_job_description(jd_record.raw_text)

    return evidence_service.build_evidence_chain(
        resume=resume_profile,
        job=job_profile,
        db=db,
    )

