"""
Document ingestion package exports for CareerCrew.
"""

from app.ingestion.document import NormalizedDocument
from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.docx_extractor import DOCXExtractor
from app.ingestion.text_extractor import TextExtractor
from app.ingestion.parser import DocumentParser, sanitize_filename, SecurityError

__all__ = [
    "NormalizedDocument",
    "PDFExtractor",
    "DOCXExtractor",
    "TextExtractor",
    "DocumentParser",
    "sanitize_filename",
    "SecurityError",
]
