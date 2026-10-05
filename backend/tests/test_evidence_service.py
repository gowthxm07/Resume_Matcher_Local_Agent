"""
Unit and integration tests for EvidenceService.
Verifies project registration, evidence indexing, skill verification hierarchy,
and the complete JD -> Resume -> Project -> Evidence chain.
"""

from pathlib import Path
from sqlalchemy.orm import Session
from app.services.evidence_service import evidence_service
from app.schemas.intelligence import ResumeProfile, JobProfile, SkillsInventory, CategorizedRequirement
from app.schemas.evidence import ConfidenceLevel

from app.models import Project, EvidenceRecord

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "repos"


def test_register_and_scan_project(db_session: Session):
    """Verify registering a valid directory scans and creates EvidenceRecord rows."""
    repo_path = str(FIXTURES_DIR / "python_fastapi_backend")
    project = evidence_service.register_project(
        name="Python FastAPI Backend",
        repo_path=repo_path,
        description="Core API Service",
        db=db_session,
    )

    assert project.id is not None
    assert project.name == "Python FastAPI Backend"
    assert project.status == "verified"

    # Verify EvidenceRecords exist in DB
    records = db_session.query(EvidenceRecord).filter(EvidenceRecord.project_id == project.id).all()
    assert len(records) > 0
    technologies = {r.canonical_skill.lower() for r in records}
    assert "fastapi" in technologies
    assert "sqlalchemy" in technologies



def test_skill_verification_hierarchy(db_session: Session):
    """
    Verify confidence hierarchy:
    - FastAPI (in requirements.txt + main.py) -> VERIFIED
    - Documentation only -> WEAK
    - Absent skill -> UNVERIFIED
    """
    # Register fastAPI repo
    evidence_service.register_project(
        name="FastAPI Service",
        repo_path=str(FIXTURES_DIR / "python_fastapi_backend"),
        description="",
        db=db_session,
    )

    # 1. VERIFIED case
    fastapi_res = evidence_service.verify_skill("FastAPI", db_session)
    assert fastapi_res.status == "VERIFIED"
    assert fastapi_res.confidence >= 0.85
    assert len(fastapi_res.projects) > 0

    # 2. UNVERIFIED case
    rust_res = evidence_service.verify_skill("Rust", db_session)
    assert rust_res.status == "UNVERIFIED"
    assert rust_res.confidence == 0.0
    assert len(rust_res.projects) == 0


def test_documentation_only_weak_verification(db_session: Session):
    """Verify skill present ONLY in README gets WEAK status (<= 0.45)."""
    evidence_service.register_project(
        name="Misleading Repo",
        repo_path=str(FIXTURES_DIR / "misleading_readme"),
        description="",
        db=db_session,
    )

    k8s_res = evidence_service.verify_skill("Kubernetes", db_session)
    # Since only present in README with no yaml manifests
    assert k8s_res.status == "WEAK"
    assert k8s_res.confidence <= 0.45


def test_build_evidence_chain_integration(db_session: Session):
    """
    Verify complete 4-part chain:
    Job Requirement -> Resume Claim -> Project -> EvidenceRecord
    """
    # Register postgres/docker project
    evidence_service.register_project(
        name="Postgres Docker Project",
        repo_path=str(FIXTURES_DIR / "postgres_docker"),
        description="",
        db=db_session,
    )

    # Construct Resume Profile claiming PostgreSQL
    resume = ResumeProfile(
        candidate_name="Alex Dev",
        skills=SkillsInventory(
            languages=["Python", "TypeScript"],
            frameworks=["FastAPI"],
            databases=["PostgreSQL"],
            tools=["Docker"],
        ),
    )

    # Construct Job Profile requiring PostgreSQL and Kubernetes
    job = JobProfile(
        title="Senior Backend Engineer",
        required_skills=["PostgreSQL", "Kubernetes"],
        categorized_requirements=[
            CategorizedRequirement(
                canonical_skill="postgresql",
                original_text="Proficiency with PostgreSQL databases and relational schema design",
                importance="required",
            ),
            CategorizedRequirement(
                canonical_skill="kubernetes",
                original_text="Experience orchestrating containers with Kubernetes",
                importance="required",
            ),
        ],
    )


    assessment = evidence_service.build_evidence_chain(resume=resume, job=job, db=db_session)

    assert assessment.scanned_projects_count >= 1
    assert len(assessment.chain) >= 2

    # PostgreSQL item should be VERIFIED
    pg_item = next(c for c in assessment.chain if c.canonical_skill == "postgresql")
    assert pg_item.resume_claimed is True
    assert pg_item.verification_status == "VERIFIED"
    assert pg_item.verification_confidence >= 0.85
    assert len(pg_item.repository_evidence) > 0
    assert "Postgres Docker Project" in pg_item.projects_found

    # Kubernetes item should be UNVERIFIED
    k8s_item = next(c for c in assessment.chain if c.canonical_skill == "kubernetes")
    assert k8s_item.verification_status == "UNVERIFIED"

    # Evidence confidence score is calculated independently
    assert assessment.evidence_confidence_score > 0.0
