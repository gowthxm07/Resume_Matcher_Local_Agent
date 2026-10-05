"""
Unified document ingestion parser and file security sanitizer for CareerCrew.
Routes files to the appropriate extractor based on validated file extension.
"""

from pathlib import Path
import re
from typing import Union
from app.core.config import settings
from app.core.logging import logger
from app.ingestion.document import NormalizedDocument
from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.docx_extractor import DOCXExtractor
from app.ingestion.text_extractor import TextExtractor


class SecurityError(Exception):
    """Raised when file validation or path sanitization detects a security risk."""
    pass


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename against path traversal, control characters, and null bytes.
    Preserves extension while replacing unsafe chars with underscores.
    """
    # Strip directory components (e.g. ../ or /etc/)
    clean = Path(filename).name
    # Remove null bytes
    clean = clean.replace("\x00", "")
    # Remove unsafe shell / filesystem characters
    clean = re.sub(r'[^a-zA-Z0-9_\-\.\s]', '_', clean)
    clean = clean.strip()
    if not clean:
        return "unnamed_document"
    return clean


class DocumentParser:
    """
    High-level entry point for ingesting and extracting text from documents.
    """

    @classmethod
    def parse_file(cls, file_path: Union[str, Path]) -> NormalizedDocument:
        """Parse document from an existing filesystem path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        file_size = path.stat().st_size
        if file_size > settings.UPLOAD_MAX_BYTES:
            raise SecurityError(
                f"File size {file_size} bytes exceeds maximum allowed {settings.UPLOAD_MAX_BYTES} bytes"
            )

        filename = sanitize_filename(path.name)
        ext = path.suffix.lower()

        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Allowed extensions: {settings.ALLOWED_FILE_EXTENSIONS}"
            )

        if ext == ".pdf":
            return PDFExtractor.extract(path, filename)
        elif ext == ".docx":
            return DOCXExtractor.extract(path, filename)
        elif ext == ".txt":
            return TextExtractor.extract(path, filename, doc_type="txt")
        elif ext == ".md":
            return TextExtractor.extract(path, filename, doc_type="md")
        else:
            raise ValueError(f"No extractor registered for extension '{ext}'")

    @classmethod
    def parse_bytes(cls, raw_bytes: bytes, original_filename: str) -> NormalizedDocument:
        """Parse document directly from in-memory byte buffer (e.g. from an upload)."""
        if len(raw_bytes) > settings.UPLOAD_MAX_BYTES:
            raise SecurityError(
                f"File size {len(raw_bytes)} bytes exceeds maximum allowed {settings.UPLOAD_MAX_BYTES} bytes"
            )

        clean_name = sanitize_filename(original_filename)
        ext = Path(clean_name).suffix.lower()

        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Allowed extensions: {settings.ALLOWED_FILE_EXTENSIONS}"
            )

        if ext == ".pdf":
            return PDFExtractor.extract(raw_bytes, clean_name)
        elif ext == ".docx":
            return DOCXExtractor.extract(raw_bytes, clean_name)
        elif ext == ".txt":
            return TextExtractor.extract(raw_bytes, clean_name, doc_type="txt")
        elif ext == ".md":
            return TextExtractor.extract(raw_bytes, clean_name, doc_type="md")
        else:
            raise ValueError(f"No extractor registered for extension '{ext}'")
