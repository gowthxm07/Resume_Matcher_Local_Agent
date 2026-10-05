"""
SQLAlchemy model representing a target Job Description (JD).
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now


class JobDescription(Base):
    """Target Job Description entity stored locally."""

    __tablename__ = "job_descriptions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled Position")
    company: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown Company")
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, extracted, analyzed, archived
    parsed_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    applications = relationship(
        "Application", back_populates="job_description", cascade="all, delete-orphan"
    )
    analysis_runs = relationship(
        "AnalysisRun", back_populates="job_description", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JobDescription id={self.id} title={self.title} company={self.company}>"
