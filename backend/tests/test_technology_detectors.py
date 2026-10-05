"""
Unit tests for modular technology detectors.
Verifies package.json, python manifests, docker/k8s configs, database schemas,
source code comment stripping, documentation confidence caps, and deduplication.
"""

from pathlib import Path
from app.services.detectors.package_json_detector import PackageJsonDetector
from app.services.detectors.python_detector import PythonDetector
from app.services.detectors.container_infra_detector import ContainerInfraDetector
from app.services.detectors.database_detector import DatabaseDetector
from app.services.detectors.documentation_detector import DocumentationDetector
from app.services.detectors.source_code_detector import SourceCodeDetector
from app.services.detectors import detector_registry

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "repos"


def test_package_json_detector():
    """Verify package.json detector extracts React, Next.js, Tailwind, and TypeScript."""
    repo = FIXTURES_DIR / "react_nextjs_app"
    detector = PackageJsonDetector()
    items = detector.detect(repo, "p-1")
    tech_names = {item.technology for item in items}

    assert "Next.js" in tech_names
    assert "React" in tech_names
    assert "Tailwind CSS" in tech_names
    assert "TypeScript" in tech_names

    # Check that Next.js has high confidence (>= 0.85 -> VERIFIED)
    next_item = next(i for i in items if i.technology == "Next.js")
    assert next_item.confidence >= 0.85
    assert next_item.confidence_level == "VERIFIED"


def test_python_detector():
    """Verify python requirements detector extracts FastAPI, SQLAlchemy, Pydantic, Pytest."""
    repo = FIXTURES_DIR / "python_fastapi_backend"
    detector = PythonDetector()
    items = detector.detect(repo, "p-2")
    tech_names = {item.technology for item in items}

    assert "FastAPI" in tech_names
    assert "SQLAlchemy" in tech_names
    assert "Pydantic" in tech_names
    assert "PyTest" in tech_names



    fastapi_item = next(i for i in items if i.technology == "FastAPI")
    assert fastapi_item.confidence >= 0.85
    assert fastapi_item.confidence_level == "VERIFIED"


def test_container_and_infra_detector():
    """Verify Docker Compose detector identifies PostgreSQL service and Docker."""
    repo = FIXTURES_DIR / "postgres_docker"
    detector = ContainerInfraDetector()
    items = detector.detect(repo, "p-3")
    tech_names = {item.technology for item in items}

    assert "Docker" in tech_names
    assert "Docker Compose" in tech_names
    assert "PostgreSQL" in tech_names

    pg_item = next(i for i in items if i.technology == "PostgreSQL")
    assert pg_item.confidence >= 0.85
    assert pg_item.confidence_level == "VERIFIED"


def test_database_detector():
    """Verify Prisma schema detector identifies Prisma ORM and PostgreSQL provider."""
    repo = FIXTURES_DIR / "postgres_docker"
    detector = DatabaseDetector()
    items = detector.detect(repo, "p-3")
    tech_names = {item.technology for item in items}

    assert "Prisma" in tech_names
    assert "PostgreSQL" in tech_names


def test_documentation_detector_confidence_cap():
    """Verify documentation-only mentions never exceed 0.45 confidence (WEAK)."""
    repo = FIXTURES_DIR / "misleading_readme"
    detector = DocumentationDetector()
    items = detector.detect(repo, "p-4")

    assert len(items) > 0
    for item in items:
        # Strict security constraint: documentation claims cannot be VERIFIED
        assert item.confidence <= 0.45
        assert item.confidence_level == "WEAK"
        assert item.evidence_type == "documentation"


def test_source_code_comment_stripping():
    """Verify commented-out code does not produce active implementation evidence."""
    detector = SourceCodeDetector()

    python_with_comment = (
        "# import fastapi\n"
        "# from sqlalchemy import create_engine\n"
        "def hello():\n"
        "    return 'world'\n"
    )
    cleaned = detector._strip_comments_and_strings(python_with_comment, ".py")
    assert "import fastapi" not in cleaned
    assert "sqlalchemy" not in cleaned


def test_detector_registry_full_scan():
    """Verify DetectorRegistry aggregates and prioritizes strongest evidence."""
    repo = FIXTURES_DIR / "python_fastapi_backend"
    items = detector_registry.run_all_detectors(repo, "p-1")

    # FastAPI should have both dependency and source_code evidence
    fastapi_items = [i for i in items if i.canonical_skill.lower() == "fastapi"]
    assert len(fastapi_items) >= 1

    # Strongest evidence should be retained with VERIFIED status
    assert any(i.confidence_level == "VERIFIED" for i in fastapi_items)
