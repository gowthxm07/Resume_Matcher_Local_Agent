"""
Tests for iterative optimization loop, iteration bounding (MAX_ITERATIONS=3),
preservation of original resume, score regression prevention, and resume versioning audit trails.
"""

import pytest
from sqlalchemy.orm import Session
from app.services.optimization_service import OptimizationService
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.project import Project
from app.models.evidence_record import EvidenceRecord
from app.models.resume_version import ResumeVersion
from app.schemas.optimization import VersionStatus


def test_optimization_loop_preserves_original_resume(db_session: Session):
    """Verify that optimization creates new ResumeVersions and NEVER overwrites the original resume raw_text."""
    original_text = (
        "SUMMARY\nSoftware Engineer with experience in web apps.\n\n"
        "EXPERIENCE\nFull Stack Developer\n- Built an AI receptionist.\n\n"
        "EDUCATION\nB.S. in Computer Science\n"
    )
    resume = Resume(
        filename="candidate_resume.txt",
        file_path="direct://text",
        file_type="txt",
        raw_text=original_text,
        status="extracted",
    )
    jd = JobDescription(
        title="Full Stack AI Engineer",
        company="NextGen Labs",
        raw_text="Looking for a Full Stack Engineer with Next.js, Express, PostgreSQL, and Ollama.",
    )
    project = Project(
        name="AI Receptionist",
        repo_path="/mock/ai-receptionist",
        evidence_metadata={"technologies": ["next.js", "express", "postgresql", "ollama"]},
    )
    db_session.add_all([resume, jd, project])
    db_session.commit()

    # Add verified evidence records
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

    service = OptimizationService()
    response = service.run_optimization(
        resume_id=resume.id,
        job_description_id=jd.id,
        project_ids=[project.id],
        max_iterations=3,
        db=db_session,
    )

    # 1. Original resume raw_text must remain strictly UNCHANGED
    db_session.refresh(resume)
    assert resume.raw_text == original_text

    # 2. Iteration 0 version must be saved as ORIGINAL
    ver_0 = (
        db_session.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume.id, ResumeVersion.iteration == 0)
        .first()
    )
    assert ver_0 is not None
    assert ver_0.status == VersionStatus.ORIGINAL.value
    assert ver_0.content == original_text

    # 3. New versions were created
    assert len(response.versions) >= 2
    assert response.dossier.iterations_run <= 3
    assert response.final_version.status in (VersionStatus.FINAL.value, VersionStatus.ACCEPTED.value)


def test_optimization_iteration_bounded_to_max_three(db_session: Session):
    """Verify that requesting > 3 iterations is strictly capped at MAX_ITERATIONS = 3."""
    resume = Resume(
        filename="test.txt",
        file_path="direct://text",
        file_type="txt",
        raw_text="EXPERIENCE\nDeveloper\n- Built an AI receptionist.\n",
    )
    jd = JobDescription(
        title="Engineer",
        raw_text="Requires Next.js, Express, PostgreSQL, Ollama.",
    )
    db_session.add_all([resume, jd])
    db_session.commit()

    service = OptimizationService()
    # Request 10 iterations (must be bounded to 3)
    response = service.run_optimization(
        resume_id=resume.id,
        job_description_id=jd.id,
        project_ids=[],
        max_iterations=10,
        db=db_session,
    )

    assert response.dossier.max_iterations == 3
    assert response.dossier.iterations_run <= 3


def test_audit_trail_explains_every_modification(db_session: Session):
    """Verify that every change has an explainable reason, original text, proposed text, and status."""
    resume = Resume(
        filename="audit_test.txt",
        file_path="direct://text",
        file_type="txt",
        raw_text="EXPERIENCE\nDeveloper\n- Built an AI receptionist.\n",
    )
    jd = JobDescription(
        title="Full Stack Engineer",
        raw_text="Requires Next.js, Express, PostgreSQL, Ollama.",
    )
    project = Project(
        name="AI Receptionist",
        repo_path="/mock/ai-receptionist",
        evidence_metadata={"technologies": ["next.js", "express", "postgresql", "ollama"]},
    )
    db_session.add_all([resume, jd, project])
    db_session.commit()

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

    service = OptimizationService()
    response = service.run_optimization(
        resume_id=resume.id,
        job_description_id=jd.id,
        project_ids=[project.id],
        max_iterations=2,
        db=db_session,
    )

    audit_trail = response.dossier.audit_trail
    assert len(audit_trail) > 0
    for entry in audit_trail:
        assert "change_id" in entry
        assert "original_text" in entry
        assert "proposed_text" in entry
        assert "status" in entry
        assert "reason" in entry


def test_zero_repository_confidence_preserved(db_session: Session):
    """Verify that with zero repositories, evidence confidence remains 0.0 and does not fabricate score."""
    resume = Resume(
        filename="no_repos.txt",
        file_path="direct://text",
        file_type="txt",
        raw_text="EXPERIENCE\nDeveloper\n- Built web tools.\n",
    )
    jd = JobDescription(
        title="Software Engineer",
        raw_text="Looking for Python developer.",
    )
    db_session.add_all([resume, jd])
    db_session.commit()

    service = OptimizationService()
    response = service.run_optimization(
        resume_id=resume.id,
        job_description_id=jd.id,
        project_ids=[],  # Explicitly zero repositories
        max_iterations=1,
        db=db_session,
    )

    assert response.dossier.baseline_evidence_confidence == 0.0
    assert response.dossier.final_evidence_confidence == 0.0
