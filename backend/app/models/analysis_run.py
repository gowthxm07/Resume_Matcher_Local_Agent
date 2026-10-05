"""
SQLAlchemy model representing an execution run of the multi-agent career intelligence pipeline.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now


class AnalysisRun(Base):
    """Analysis run tracking multi-agent iteration metrics and results."""

    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    application_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True
    )
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_description_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="initial_assessment"
    )  # initial_assessment, match_scoring, optimization_loop, interview_prep
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, running, completed, failed
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    results_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    resume = relationship("Resume", back_populates="analysis_runs")
    job_description = relationship("JobDescription", back_populates="analysis_runs")
    application = relationship("Application", back_populates="analysis_runs")

    def __repr__(self) -> str:
        return f"<AnalysisRun id={self.id} type={self.run_type} status={self.status} score={self.match_score}>"
