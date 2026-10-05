"""
Database initialization and health verification utility for CareerCrew.
Creates all SQLite tables and provides status introspection.
Includes automatic lightweight column migrations for backward compatibility.
"""

from typing import Dict, Any, List
from sqlalchemy import inspect, text
from app.db.base import Base
from app.db.session import engine
from app.models import Resume, JobDescription, Project, Application, AnalysisRun, EvidenceRecord
from app.core.logging import logger


def init_db(target_engine=None) -> None:
    """Initialize all registered SQLAlchemy tables in the local SQLite database."""
    eng = target_engine or engine
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=eng)

    # Lightweight SQLite column migration for Phase 3 Project columns and Phase 4 AnalysisRun columns
    try:
        with eng.connect() as conn:
            inspector = inspect(eng)
            table_names = inspector.get_table_names()
            if "projects" in table_names:
                columns = {c["name"] for c in inspector.get_columns("projects")}
                if "git_remote" not in columns:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN git_remote VARCHAR(512)"))
                if "git_branch" not in columns:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN git_branch VARCHAR(255)"))
                if "head_commit" not in columns:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN head_commit VARCHAR(64)"))
                if "commit_count" not in columns:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN commit_count INTEGER DEFAULT 0"))
                if "last_scanned_at" not in columns:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN last_scanned_at DATETIME"))
            if "analysis_runs" in table_names:
                ar_columns = {c["name"] for c in inspector.get_columns("analysis_runs")}
                if "execution_mode" not in ar_columns:
                    conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN execution_mode VARCHAR(50)"))
                if "evidence_confidence" not in ar_columns:
                    conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN evidence_confidence FLOAT"))
            conn.commit()
    except Exception as exc:
        logger.warning(f"Note during SQLite table migration: {exc}")

    logger.info("Database tables initialized successfully.")


def check_db_health(target_engine=None) -> Dict[str, Any]:
    """Inspect database connectivity and table schema health."""
    try:
        eng = target_engine or engine
        inspector = inspect(eng)
        existing_tables: List[str] = inspector.get_table_names()
        expected_tables = [
            "resumes",
            "job_descriptions",
            "projects",
            "applications",
            "analysis_runs",
            "evidence_records",
        ]
        all_present = all(t in existing_tables for t in expected_tables)

        return {
            "status": "healthy" if all_present else "degraded",
            "connected": True,
            "engine": "sqlite",
            "tables": existing_tables,
            "all_expected_tables_present": all_present,
            "expected_tables": expected_tables,
        }
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(exc),
            "tables": [],
        }
