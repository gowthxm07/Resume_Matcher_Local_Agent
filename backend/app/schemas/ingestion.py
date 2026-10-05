"""
Pydantic schemas for document ingestion and text extraction.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata extracted or associated with a document."""
    file_size_bytes: int = 0
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    author: Optional[str] = None
    title: Optional[str] = None
    creation_date: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class NormalizedDocument(BaseModel):
    """
    Standard normalized document representation across all supported file types
    (PDF, DOCX, TXT, Markdown).
    """
    document_id: str = Field(description="Unique identifier for the document")
    filename: str = Field(description="Sanitized original filename")
    document_type: str = Field(description="File format extension: pdf, docx, txt, md")
    extracted_text: str = Field(description="Raw extracted plain text content")
    character_count: int = Field(description="Total characters extracted")
    word_count: int = Field(description="Total word count")
    page_count: Optional[int] = Field(default=None, description="Page count if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    extraction_time_ms: float = Field(default=0.0, description="Time taken to extract in ms")


class IngestionResponse(BaseModel):
    """API response for document ingestion."""
    success: bool
    document: Optional[NormalizedDocument] = None
    error: Optional[str] = None
