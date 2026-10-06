"""
SQLAlchemy model representing an immutable version of an optimized candidate resume.
Preserves the complete audit trail and guarantees the original resume is never overwritten.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now


class ResumeVersion(Base):
    """Resume version entity capturing iterative optimizations and audit status."""

    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    analysis_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ats_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ORIGINAL"
    )  # ORIGINAL, CANDIDATE, ACCEPTED, REJECTED, FINAL
    change_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    audit_trail: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON, nullable=True, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    resume = relationship("Resume", back_populates="versions")
    analysis_run = relationship("AnalysisRun", back_populates="resume_versions")

    def __repr__(self) -> str:
        return (
            f"<ResumeVersion id={self.id} resume_id={self.resume_id} "
            f"iteration={self.iteration} status={self.status} match={self.match_score} ats={self.ats_score}>"
        )
