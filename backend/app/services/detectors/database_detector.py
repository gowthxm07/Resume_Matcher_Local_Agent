"""
Database schema, migration, and ORM technology detector.
Inspects Prisma schemas, SQL migration files, and database configs for concrete DB evidence.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer
from app.core.logging import logger

PRISMA_PROVIDER_MAP = {
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "cockroachdb": "PostgreSQL",
}


class DatabaseDetector(BaseDetector):
    """Detects database engines and ORMs from schemas, migrations, and configs."""

    name = "database_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # 1. Prisma Schema detection
        prisma_candidates = [
            repo_path / "prisma" / "schema.prisma",
            repo_path / "schema.prisma",
        ]

        for p_file in prisma_candidates:
            if p_file.is_file():
                rel_path = str(p_file.relative_to(repo_path))
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Prisma",
                        canonical_skill=skill_normalizer.normalize("Prisma"),
                        evidence_type=EvidenceType.DATABASE_SCHEMA.value,
                        source_file=rel_path,
                        description="Prisma database schema file present.",
                        confidence=0.99,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )

                try:
                    content = p_file.read_text(encoding="utf-8", errors="ignore")
                    # Match provider = "postgresql"
                    provider_match = re.search(r'provider\s*=\s*["\']([a-zA-Z0-9_\-]+)["\']', content)
                    if provider_match:
                        raw_prov = provider_match.group(1).lower()
                        if raw_prov in PRISMA_PROVIDER_MAP:
                            tech = PRISMA_PROVIDER_MAP[raw_prov]
                            canonical = skill_normalizer.normalize(tech)
                            items.append(
                                EvidenceItem(
                                    project_id=project_id,
                                    technology=tech,
                                    canonical_skill=canonical,
                                    evidence_type=EvidenceType.DATABASE_SCHEMA.value,
                                    source_file=rel_path,
                                    description=f"{tech} configured as primary datasource provider in Prisma schema.",
                                    confidence=0.98,
                                    confidence_level=ConfidenceLevel.VERIFIED.value,
                                    detector=self.name,
                                    snippet=provider_match.group(0).strip(),
                                )
                            )
                except Exception as exc:
                    logger.warning(f"Error parsing {rel_path} in '{repo_path}': {exc}")
                break

        # 2. Alembic migration detection
        alembic_ini = repo_path / "alembic.ini"
        if alembic_ini.is_file():
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Alembic",
                    canonical_skill=skill_normalizer.normalize("Alembic"),
                    evidence_type=EvidenceType.CONFIGURATION.value,
                    source_file="alembic.ini",
                    description="Alembic database migration configuration present.",
                    confidence=0.98,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

        # 3. SQL migration files
        sql_files = list(repo_path.glob("**/*.sql"))
        # Exclude node_modules, .venv, etc.
        sql_files = [
            f for f in sql_files
            if not any(part in f.parts for part in ["node_modules", ".venv", "venv", "dist", "build"])
        ]

        if sql_files:
            rel_sql = str(sql_files[0].relative_to(repo_path))
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="SQL",
                    canonical_skill=skill_normalizer.normalize("SQL"),
                    evidence_type=EvidenceType.DATABASE_SCHEMA.value,
                    source_file=rel_sql,
                    description=f"Raw SQL migration/schema files defined ({len(sql_files)} file(s)).",
                    confidence=0.95,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

            # Check for PostgreSQL-specific keywords in SQL files
            for sf in sql_files[:5]:
                try:
                    sql_content = sf.read_text(encoding="utf-8", errors="ignore")[:2000].lower()
                    if any(kw in sql_content for kw in ["uuid-ossp", "timestamptz", "bytea", "serial primary key", "create extension"]):
                        items.append(
                            EvidenceItem(
                                project_id=project_id,
                                technology="PostgreSQL",
                                canonical_skill=skill_normalizer.normalize("PostgreSQL"),
                                evidence_type=EvidenceType.DATABASE_SCHEMA.value,
                                source_file=str(sf.relative_to(repo_path)),
                                description="PostgreSQL-specific dialect keywords detected in SQL schema/migration.",
                                confidence=0.95,
                                confidence_level=ConfidenceLevel.VERIFIED.value,
                                detector=self.name,
                            )
                        )
                        break
                except Exception:
                    pass

        return items
