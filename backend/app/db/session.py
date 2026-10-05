"""
Database session management for SQLite.
Ensures local thread-safe session lifecycle and directory creation.
"""

from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger


# Ensure the sqlite database directory exists
def _prepare_db_path(db_url: str) -> None:
    if db_url.startswith("sqlite:///"):
        raw_path = db_url.replace("sqlite:///", "")
        path = Path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)


_prepare_db_path(settings.DATABASE_URL)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session,
    ensuring rollback on exception and guaranteed close on exit.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        db.rollback()
        logger.error(f"Database session rollback due to error: {exc}")
        raise
    finally:
        db.close()
