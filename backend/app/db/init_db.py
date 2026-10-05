"""
Database initialization and health verification utility for CareerCrew.
Creates all SQLite tables and provides status introspection.
"""

from typing import Dict, Any, List
from sqlalchemy import inspect
from app.db.base import Base
from app.db.session import engine
from app.models import Resume, JobDescription, Project, Application, AnalysisRun
from app.core.logging import logger


def init_db(target_engine=None) -> None:
    """Initialize all registered SQLAlchemy tables in the local SQLite database."""
    eng = target_engine or engine
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=eng)
    logger.info("Database tables initialized successfully.")


def check_db_health(target_engine=None) -> Dict[str, Any]:
    """Inspect database connectivity and table schema health."""
    try:
        eng = target_engine or engine
        inspector = inspect(eng)
        existing_tables: List[str] = inspector.get_table_names()
        expected_tables = ["resumes", "job_descriptions", "projects", "applications", "analysis_runs"]
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
