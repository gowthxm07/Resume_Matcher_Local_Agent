"""
Normalized document data representation for CareerCrew ingestion pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid


@dataclass
class NormalizedDocument:
    """
    Unified representation of any extracted text document (Resume, JD, Project Doc).
    """

    filename: str
    document_type: str  # pdf, docx, txt, md
    extracted_text: str
    document_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    metadata: Dict[str, Any] = field(default_factory=dict)
    character_count: int = 0
    word_count: int = 0
    page_count: Optional[int] = None
    extraction_time_ms: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self):
        if not self.character_count:
            self.character_count = len(self.extracted_text)
        if not self.word_count:
            self.word_count = len(self.extracted_text.split())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "document_type": self.document_type,
            "extracted_text": self.extracted_text,
            "character_count": self.character_count,
            "word_count": self.word_count,
            "page_count": self.page_count,
            "metadata": self.metadata,
            "extraction_time_ms": self.extraction_time_ms,
            "created_at": self.created_at,
        }
