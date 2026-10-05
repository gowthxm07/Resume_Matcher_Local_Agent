"""
Source code pattern and import analysis detector.
Inspects real application source files (*.py, *.ts, *.tsx, *.js, *.jsx) for actual imports
and object initializations.
CRITICAL RULE: Strips comments and docstrings to prevent false positives from incidental text.
"""

import re
from pathlib import Path
from typing import List, Set, Tuple
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer

IGNORE_DIRS = {
    "node_modules", "venv", ".venv", "env", "dist", "build", ".next",
    ".git", "__pycache__", "coverage", "target", ".pytest_cache"
}

# Regex patterns for stripping comments
PYTHON_COMMENT_RE = re.compile(r"#.*$", re.MULTILINE)
PYTHON_DOCSTRING_RE = re.compile(r'""".*?"""|\'\'\'.*?\'\'\'', re.DOTALL)
JS_SINGLE_COMMENT_RE = re.compile(r"//.*$", re.MULTILINE)
JS_MULTI_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

# Concrete import signatures that guarantee real code usage
SOURCE_SIGNATURES: List[Tuple[str, str, str, str]] = [
    # (Regex pattern, Technology, Extension filter, Description)
    (r"\bfrom\s+fastapi\s+import\b|\bimport\s+fastapi\b", "FastAPI", ".py", "Active FastAPI framework import statement."),
    (r"\bfrom\s+sqlalchemy\s+import\b|\bimport\s+sqlalchemy\b", "SQLAlchemy", ".py", "Active SQLAlchemy ORM import statement."),
    (r"\bfrom\s+pydantic\s+import\b|\bimport\s+pydantic\b", "Pydantic", ".py", "Active Pydantic schema validation import."),
    (r"\bimport\s+psycopg2\b|\bimport\s+asyncpg\b", "PostgreSQL", ".py", "Active PostgreSQL database driver import."),
    (r"\bimport\s+redis\b|\bfrom\s+redis\s+import\b", "Redis", ".py", "Active Redis client import."),
    (r"\bfrom\s+django\s+import\b|\bimport\s+django\b", "Django", ".py", "Active Django framework import."),
    (r"\bfrom\s+flask\s+import\b|\bimport\s+flask\b", "Flask", ".py", "Active Flask microframework import."),
    (r"""\bfrom\s+['"]react['"]|\bimport\s+React\b""", "React", ".ts,.tsx,.js,.jsx", "Active React component library import."),
    (r"""\bfrom\s+['"]next/[a-zA-Z0-9_\-]+['"]""", "Next.js", ".ts,.tsx,.js,.jsx", "Active Next.js routing/component import."),
    (r"""\bfrom\s+['"]express['"]|\brequire\(['"]express['"]\)""", "Express", ".ts,.js", "Active Express application import."),
    (r"""\bfrom\s+['"]@prisma/client['"]""", "Prisma", ".ts,.js", "Active Prisma client ORM import."),
    (r"""\bfrom\s+['"]pg['"]|\brequire\(['"]pg['"]\)""", "PostgreSQL", ".ts,.js", "Active PostgreSQL client driver import."),
]


def strip_comments(content: str, ext: str) -> str:
    """Remove comments and docstrings before scanning to prevent comment false positives."""
    if ext == ".py":
        without_docs = PYTHON_DOCSTRING_RE.sub("", content)
        return PYTHON_COMMENT_RE.sub("", without_docs)
    elif ext in [".ts", ".tsx", ".js", ".jsx"]:
        without_multi = JS_MULTI_COMMENT_RE.sub("", content)
        return JS_SINGLE_COMMENT_RE.sub("", without_multi)
    return content


class SourceCodeDetector(BaseDetector):
    """Inspects active imports in source code files while ignoring comments and text."""

    name = "source_code_detector"
    _strip_comments_and_strings = staticmethod(strip_comments)

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:

        items: List[EvidenceItem] = []
        found_techs: Set[str] = set()

        # Recursively find source files up to reasonable limit
        scanned_count = 0
        max_files_to_scan = 60

        for path in repo_path.rglob("*"):
            if scanned_count >= max_files_to_scan:
                break

            # Skip ignored directories
            if any(part in IGNORE_DIRS for part in path.parts):
                continue

            if not path.is_file():
                continue

            ext = path.suffix.lower()
            if ext not in [".py", ".ts", ".tsx", ".js", ".jsx"]:
                continue

            try:
                raw_text = path.read_text(encoding="utf-8", errors="ignore")[:10000]
                cleaned_text = strip_comments(raw_text, ext)

                for pattern, tech, allowed_exts, desc in SOURCE_SIGNATURES:
                    if tech in found_techs:
                        continue

                    if ext in allowed_exts.split(","):
                        match = re.search(pattern, cleaned_text)
                        if match:
                            found_techs.add(tech)
                            rel_file = str(path.relative_to(repo_path))
                            canonical = skill_normalizer.normalize(tech)
                            items.append(
                                EvidenceItem(
                                    project_id=project_id,
                                    technology=tech,
                                    canonical_skill=canonical,
                                    evidence_type=EvidenceType.SOURCE_CODE.value,
                                    source_file=rel_file,
                                    description=f"{desc} Found in {rel_file}.",
                                    confidence=0.96,
                                    confidence_level=ConfidenceLevel.VERIFIED.value,
                                    detector=self.name,
                                    snippet=match.group(0).strip(),
                                )
                            )

                scanned_count += 1
            except Exception:
                continue

        return items
