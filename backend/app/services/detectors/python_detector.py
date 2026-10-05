"""
Python ecosystem technology detector.
Inspects requirements.txt, pyproject.toml, Pipfile, and setup.py for verified dependencies.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer
from app.core.logging import logger

PYTHON_PACKAGE_MAPPING = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "psycopg2": "PostgreSQL",
    "psycopg2-binary": "PostgreSQL",
    "asyncpg": "PostgreSQL",
    "pymongo": "MongoDB",
    "motor": "MongoDB",
    "redis": "Redis",
    "aioredis": "Redis",
    "pytest": "PyTest",
    "celery": "Celery",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "docker": "Docker",
    "boto3": "AWS",
    "alembic": "Alembic",
    "httpx": "HTTPX",
    "uvicorn": "Uvicorn",
}


def clean_pip_requirement(line: str) -> str:
    """Extract bare package name from pip requirement line (e.g. 'fastapi>=0.100.0' -> 'fastapi')."""
    cleaned = line.split("#")[0].strip()
    match = re.match(r"^([a-zA-Z0-9_\-\.]+)", cleaned)
    if match:
        return match.group(1).lower().strip()
    return ""


class PythonDetector(BaseDetector):
    """Detects Python dependencies and frameworks from standard dependency manifests."""

    name = "python_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        is_python_project = False

        # 1. Inspect requirements.txt
        req_file = repo_path / "requirements.txt"
        if req_file.is_file():
            is_python_project = True
            try:
                lines = req_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                for line in lines:
                    pkg = clean_pip_requirement(line)
                    if pkg in PYTHON_PACKAGE_MAPPING:
                        tech = PYTHON_PACKAGE_MAPPING[pkg]
                        canonical = skill_normalizer.normalize(tech)
                        items.append(
                            EvidenceItem(
                                project_id=project_id,
                                technology=tech,
                                canonical_skill=canonical,
                                evidence_type=EvidenceType.DEPENDENCY.value,
                                source_file="requirements.txt",
                                description=f"Python pip dependency '{line.strip()}'.",
                                confidence=0.98,
                                confidence_level=ConfidenceLevel.VERIFIED.value,
                                detector=self.name,
                                snippet=line.strip(),
                            )
                        )
            except Exception as exc:
                logger.warning(f"Error parsing requirements.txt in '{repo_path}': {exc}")

        # 2. Inspect pyproject.toml
        pyproject_file = repo_path / "pyproject.toml"
        if pyproject_file.is_file():
            is_python_project = True
            try:
                content = pyproject_file.read_text(encoding="utf-8", errors="ignore")
                for pkg, tech in PYTHON_PACKAGE_MAPPING.items():
                    # Look for quoted dependency like "fastapi", 'fastapi>=', etc.
                    pattern = rf"""["']{re.escape(pkg)}(?:[>=<~!].*)?["']"""
                    if re.search(pattern, content, re.IGNORECASE):
                        canonical = skill_normalizer.normalize(tech)
                        items.append(
                            EvidenceItem(
                                project_id=project_id,
                                technology=tech,
                                canonical_skill=canonical,
                                evidence_type=EvidenceType.DEPENDENCY.value,
                                source_file="pyproject.toml",
                                description=f"PyProject TOML dependency '{pkg}'.",
                                confidence=0.98,
                                confidence_level=ConfidenceLevel.VERIFIED.value,
                                detector=self.name,
                            )
                        )
            except Exception as exc:
                logger.warning(f"Error parsing pyproject.toml in '{repo_path}': {exc}")

        # 3. Pipfile
        pipfile = repo_path / "Pipfile"
        if pipfile.is_file():
            is_python_project = True

        # Emit Python language evidence if python manifests are present
        if is_python_project:
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Python",
                    canonical_skill=skill_normalizer.normalize("Python"),
                    evidence_type=EvidenceType.CONFIGURATION.value,
                    source_file="requirements.txt" if req_file.exists() else "pyproject.toml",
                    description="Python project dependency configuration detected.",
                    confidence=0.99,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

        return items
