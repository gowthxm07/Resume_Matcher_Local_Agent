"""
SQLAlchemy model representing an atomic piece of repository evidence.
Grounds candidate technical claims in real local files, configurations, and commits.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now


class EvidenceRecord(Base):
    """
    Individual evidence item extracted from a candidate's local repository.
    Verifies a specific technical skill or architectural claim.
    """

    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    technology: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    canonical_skill: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # dependency, configuration, source_code, database_schema, infrastructure, documentation, git_history, test, build
    source_file: Mapped[str] = mapped_column(String(512), nullable=False)
    source_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    confidence_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="UNVERIFIED"
    )  # VERIFIED, LIKELY, WEAK, UNVERIFIED
    detector: Mapped[str] = mapped_column(String(100), nullable=False, default="generic")
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    project = relationship("Project", back_populates="evidence_records")

    def __repr__(self) -> str:
        return f"<EvidenceRecord id={self.id} tech={self.technology} type={self.evidence_type} conf={self.confidence_level}>"
