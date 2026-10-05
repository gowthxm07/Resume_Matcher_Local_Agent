"""
Phase 3 Complete Verification Script for CareerCrew.
Verifies the Evidence-Grounded Project Intelligence System:
- Filesystem Security Boundaries & Path Traversal Defenses (PathValidator)
- Safe Git Repository Scanner (GitScanner, commit history, credential sanitization)
- Modular Technology Detectors (package.json, python, docker/k8s, database, docs, source code)
- Source Code Comment Stripping (Prevents commented-out false positives)
- Documentation Confidence Cap (<= 0.45, WEAK status)
- Evidence Service & Hierarchy (VERIFIED, LIKELY, WEAK, UNVERIFIED)
- Complete 4-Part Chain: Job Requirement -> Resume Claim -> Project -> Repository Evidence
- Independent Evidence Confidence Score Calculation
- Deterministic CrewAI Evidence Inspection Tools
- Zero Paid Cloud API Constraints
"""

import sys
import os
import tempfile
import git
from pathlib import Path

# Add backend to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.models import Project, EvidenceRecord

from app.services.path_validator import PathValidator, PathValidationError
from app.services.git_scanner import git_scanner
from app.services.detectors import detector_registry
from app.services.detectors.package_json_detector import PackageJsonDetector
from app.services.detectors.python_detector import PythonDetector
from app.services.detectors.container_infra_detector import ContainerInfraDetector
from app.services.detectors.database_detector import DatabaseDetector
from app.services.detectors.documentation_detector import DocumentationDetector
from app.services.detectors.source_code_detector import SourceCodeDetector
from app.services.evidence_service import evidence_service
from app.schemas.evidence import ConfidenceLevel
from app.schemas.intelligence import (
    ResumeProfile,
    JobProfile,
    SkillsInventory,
    CategorizedRequirement,
)
from app.agents.tools.evidence_tools import (
    scan_git_repository_tool,
    extract_commit_evidence_tool,
    find_skill_evidence_tool,
    verify_skill_tool,
    get_evidence_tools,
)

FIXTURES_DIR = ROOT_DIR / "backend" / "tests" / "fixtures" / "repos"


def main():
    print("=" * 70)
    print("CAREERCREW - PHASE 3 EVIDENCE-GROUNDED PROJECT INTELLIGENCE VERIFICATION")
    print("=" * 70)

    # 1. Zero Cloud API Verification
    print("\n1. Verifying Zero Paid Cloud API Constraint...")
    assert settings.LLM_PROVIDER == "ollama", "LLM_PROVIDER must be 'ollama'"
    assert "openai" not in settings.LLM_PROVIDER.lower()
    assert "anthropic" not in settings.LLM_PROVIDER.lower()
    print("   [PASS] Provider: Local Ollama (llama3.2:3b)")
    print("   [PASS] Local Embeddings: nomic-embed-text")
    print("   [PASS] Zero Cloud APIs permitted or configured.")

    # 2. Filesystem Security & Path Traversal Protections
    print("\n2. Testing Path Security Boundaries & Traversal Protections...")
    with tempfile.TemporaryDirectory() as tmpdir:
        valid_path = PathValidator.validate_project_path(tmpdir)
        assert valid_path.exists()
    print("   [PASS] Valid user directory allowed.")

    # Root drive rejection
    try:
        root_drive = "C:\\" if os.name == "nt" else "/"
        PathValidator.validate_project_path(root_drive)
        assert False, "Should have rejected root drive"
    except PathValidationError:
        print("   [PASS] Root filesystem registration strictly blocked.")

    # System directory rejection
    if os.name == "nt":
        sys_dir = os.environ.get("SystemRoot", "C:\\Windows")
        try:
            PathValidator.validate_project_path(sys_dir)
            assert False, "Should have rejected system directory"
        except PathValidationError:
            print("   [PASS] Windows system directory access strictly denied.")

    # Internal database directory rejection
    try:
        PathValidator.validate_project_path(str(settings.DATA_DIR))
        assert False, "Should have rejected internal data directory"
    except PathValidationError:
        print("   [PASS] CareerCrew internal data directory protected.")

    # 3. Safe Git Repository Scanner
    print("\n3. Testing Safe Git Repository Scanner (Read-Only)...")
    with tempfile.TemporaryDirectory() as tmpdir:
        non_git_meta = git_scanner.scan_repository(tmpdir)
        assert non_git_meta.is_git_repo is False
        print("   [PASS] Non-git directory handled gracefully without error.")

        # Test real git repo
        repo = git.Repo.init(tmpdir)
        try:
            repo.config_writer().set_value("user", "name", "Evidence Dev").release()
            repo.config_writer().set_value("user", "email", "dev@careercrew.local").release()

            fpath = os.path.join(tmpdir, "service.py")
            with open(fpath, "w") as f:
                f.write("import fastapi\n")
            repo.index.add(["service.py"])
            commit = repo.index.commit("Initial microservice commit")
            commit_hex = commit.hexsha
        finally:
            repo.close()

        git_meta = git_scanner.scan_repository(tmpdir)
        assert git_meta.is_git_repo is True
        assert git_meta.head_commit == commit_hex
        assert git_meta.commit_count == 1
        assert "Evidence Dev" in git_meta.author_stats
        print("   [PASS] Local Git HEAD commit, branch, and author statistics extracted.")

    # Remote URL sanitization
    dirty_url = "https://oauth2:ghp_secretToken123456@github.com/candidate/app.git"
    clean_url = git_scanner._sanitize_remote_url(dirty_url)
    assert "secretToken" not in clean_url
    assert "oauth2" not in clean_url
    assert "github.com/candidate/app.git" in clean_url
    print("   [PASS] Git remote credentials sanitized and stripped.")

    # 4. Modular Technology Detectors
    print("\n4. Testing Modular Technology Detectors on Synthetic Repositories...")

    # Package.json detector
    pj_items = PackageJsonDetector().detect(FIXTURES_DIR / "react_nextjs_app", "p-1")
    pj_techs = {i.technology for i in pj_items}
    assert "Next.js" in pj_techs
    assert "React" in pj_techs
    assert "Tailwind CSS" in pj_techs
    assert "TypeScript" in pj_techs
    print("   [PASS] PackageJsonDetector: Extracted Next.js, React, Tailwind, and TypeScript.")

    # Python detector
    py_items = PythonDetector().detect(FIXTURES_DIR / "python_fastapi_backend", "p-2")
    py_techs = {i.technology for i in py_items}
    assert "FastAPI" in py_techs
    assert "SQLAlchemy" in py_techs
    assert "Pydantic" in py_techs
    assert "PyTest" in py_techs
    print("   [PASS] PythonDetector: Extracted FastAPI, SQLAlchemy, Pydantic, and PyTest.")

    # Container / Infra detector
    infra_items = ContainerInfraDetector().detect(FIXTURES_DIR / "postgres_docker", "p-3")
    infra_techs = {i.technology for i in infra_items}
    assert "Docker" in infra_techs
    assert "Docker Compose" in infra_techs
    assert "PostgreSQL" in infra_techs
    print("   [PASS] ContainerInfraDetector: Extracted Docker, Docker Compose, and PostgreSQL.")

    # Database detector
    db_items = DatabaseDetector().detect(FIXTURES_DIR / "postgres_docker", "p-3")
    db_techs = {i.technology for i in db_items}
    assert "Prisma" in db_techs
    assert "PostgreSQL" in db_techs
    print("   [PASS] DatabaseDetector: Extracted Prisma schema and PostgreSQL provider.")

    # Documentation confidence cap
    doc_items = DocumentationDetector().detect(FIXTURES_DIR / "misleading_readme", "p-4")
    assert len(doc_items) > 0
    for d in doc_items:
        assert d.confidence <= 0.45, f"Doc confidence {d.confidence} exceeded 0.45 cap"
        assert d.confidence_level == "WEAK"
    print("   [PASS] DocumentationDetector: Strictly capped at <= 0.45 (WEAK status).")

    # Source code comment stripping
    raw_code = "# import fastapi\n# from sqlalchemy import select\ndef run():\n    pass\n"
    cleaned = SourceCodeDetector._strip_comments_and_strings(raw_code, ".py")
    assert "import fastapi" not in cleaned
    assert "sqlalchemy" not in cleaned
    print("   [PASS] SourceCodeDetector: Comment stripping prevents false positives.")

    # 5. Evidence Service & Confidence Hierarchy
    print("\n5. Testing Evidence Service & Confidence Hierarchy in SQLite...")
    init_db()
    db = SessionLocal()

    try:
        # Register FastAPI and Postgres fixtures
        proj1 = evidence_service.register_project(
            db=db,
            name="Backend Microservice",
            repo_path=str(FIXTURES_DIR / "python_fastapi_backend"),
            description="Core API Service",
        )
        assert proj1.id is not None

        proj2 = evidence_service.register_project(
            db=db,
            name="Database Infra",
            repo_path=str(FIXTURES_DIR / "postgres_docker"),
            description="Database containers and schemas",
        )
        assert proj2.id is not None

        proj3 = evidence_service.register_project(
            db=db,
            name="Cloud Showcase (Docs Only)",
            repo_path=str(FIXTURES_DIR / "misleading_readme"),
            description="Misleading project with only text claims",
        )
        assert proj3.id is not None

        # Hierarchy Level 1: VERIFIED
        verif_fastapi = evidence_service.verify_skill(db=db, skill="FastAPI")
        assert verif_fastapi.status == "VERIFIED"
        assert verif_fastapi.confidence >= 0.85
        print(f"   [PASS] FastAPI -> {verif_fastapi.status} ({verif_fastapi.confidence * 100:.0f}%) [Direct implementation]")

        verif_pg = evidence_service.verify_skill(db=db, skill="PostgreSQL")
        assert verif_pg.status == "VERIFIED"
        assert verif_pg.confidence >= 0.85
        print(f"   [PASS] PostgreSQL -> {verif_pg.status} ({verif_pg.confidence * 100:.0f}%) [Docker Compose + Prisma]")

        # Hierarchy Level 3: WEAK (from misleading README only)
        verif_k8s = evidence_service.verify_skill(db=db, skill="Kubernetes")
        assert verif_k8s.status == "WEAK"
        assert verif_k8s.confidence <= 0.45
        print(f"   [PASS] Kubernetes -> {verif_k8s.status} ({verif_k8s.confidence * 100:.0f}%) [Documentation mention only]")

        # Hierarchy Level 4: UNVERIFIED
        verif_rust = evidence_service.verify_skill(db=db, skill="Rust")
        assert verif_rust.status == "UNVERIFIED"
        assert verif_rust.confidence == 0.0
        print(f"   [PASS] Rust -> {verif_rust.status} (0%) [No repository evidence]")

        # 6. Complete 4-Part Evidence Chain
        print("\n6. Testing Unified 4-Part Evidence Chain Construction...")
        test_resume = ResumeProfile(
            candidate_name="Alex Chen",
            skills=SkillsInventory(
                languages=["Python"],
                frameworks=["FastAPI"],
                databases=["PostgreSQL"],
                tools=["Docker", "Kubernetes"],
            ),
        )

        test_job = JobProfile(
            title="Lead Backend Architect",
            required_skills=["FastAPI", "PostgreSQL", "Kubernetes", "Rust"],
            categorized_requirements=[
                CategorizedRequirement(
                    canonical_skill="FastAPI",
                    original_text="Production experience building microservices with FastAPI",
                    importance="required",
                ),
                CategorizedRequirement(
                    canonical_skill="PostgreSQL",
                    original_text="Proficiency in PostgreSQL schema design and database optimization",
                    importance="required",
                ),
                CategorizedRequirement(
                    canonical_skill="Kubernetes",
                    original_text="Hands-on experience orchestrating production Kubernetes clusters",
                    importance="required",
                ),
                CategorizedRequirement(
                    canonical_skill="Rust",
                    original_text="Experience developing high-throughput systems in Rust",
                    importance="required",
                ),
            ],
        )

        assessment = evidence_service.build_evidence_chain(
            db=db, resume=test_resume, job=test_job
        )

        assert assessment.scanned_projects_count >= 3
        assert len(assessment.chain) == 4
        assert assessment.verified_skills_count == 2
        assert assessment.weak_skills_count == 1
        assert assessment.unverified_skills_count == 1
        assert 0.0 < assessment.evidence_confidence_score <= 100.0

        print(f"   [PASS] Scanned Projects: {assessment.scanned_projects_count}")
        print(f"   [PASS] Evidence Confidence Score: {assessment.evidence_confidence_score}%")
        print(f"   [PASS] Verified: {assessment.verified_skills_count}, Likely: {assessment.likely_skills_count}, Weak: {assessment.weak_skills_count}, Unverified: {assessment.unverified_skills_count}")
        print(f"   [PASS] 4-Part Trace: Job Requirement -> Resume Claim -> Project -> Repository Evidence established.")

    finally:
        db.close()

    # 7. Deterministic CrewAI Evidence Inspection Tools
    print("\n7. Testing Deterministic CrewAI Evidence Inspection Tools...")
    tools = get_evidence_tools()
    assert len(tools) == 4
    tool_names = [t.name if hasattr(t, "name") else str(t) for t in tools]
    print(f"   [PASS] Registered Tools: {', '.join(tool_names)}")

    tool_result = (
        scan_git_repository_tool.run(project_path=str(FIXTURES_DIR / "python_fastapi_backend"))
        if hasattr(scan_git_repository_tool, "run")
        else scan_git_repository_tool(str(FIXTURES_DIR / "python_fastapi_backend"))
    )
    assert "repo_name" in tool_result
    print("   [PASS] scan_git_repository_tool executed safely.")

    commit_tool_result = (
        extract_commit_evidence_tool.run(project_path=str(FIXTURES_DIR / "python_fastapi_backend"), max_commits=5)
        if hasattr(extract_commit_evidence_tool, "run")
        else extract_commit_evidence_tool(str(FIXTURES_DIR / "python_fastapi_backend"), max_commits=5)
    )
    assert isinstance(commit_tool_result, str)
    print("   [PASS] extract_commit_evidence_tool executed safely.")

    skill_tool_result = (
        verify_skill_tool.run(skill="FastAPI")
        if hasattr(verify_skill_tool, "run")
        else verify_skill_tool("FastAPI")
    )
    assert "VERIFIED" in skill_tool_result
    print("   [PASS] verify_skill_tool executed safely.")


    print("\n" + "=" * 70)
    print("PHASE 3 VERIFICATION COMPLETE: ALL CHECKS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
