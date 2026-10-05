"""
PDF extraction module utilizing PyMuPDF (fitz).
Provides safe text extraction, page metadata extraction, and error handling.
"""

import time
from pathlib import Path
from typing import Union
import pymupdf as fitz
from app.ingestion.document import NormalizedDocument
from app.core.logging import logger


class PDFExtractor:
    """Extracts raw text and metadata from PDF files using PyMuPDF."""

    @classmethod
    def extract(cls, file_path_or_bytes: Union[str, Path, bytes], filename: str) -> NormalizedDocument:
        """
        Extract text content and page metadata from a PDF.

        Args:
            file_path_or_bytes: Path to PDF or raw file bytes
            filename: Original filename

        Returns:
            NormalizedDocument instance
        """
        start_time = time.perf_counter()
        doc = None
        try:
            if isinstance(file_path_or_bytes, (str, Path)):
                path = Path(file_path_or_bytes)
                if not path.exists():
                    raise FileNotFoundError(f"PDF file not found at: {path}")
                doc = fitz.open(str(path))
                file_size = path.stat().st_size
            else:
                doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
                file_size = len(file_path_or_bytes)

            if doc.is_encrypted:
                raise ValueError("PDF is encrypted / password protected and cannot be processed.")

            page_texts = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                if text:
                    page_texts.append(text.strip())

            extracted_text = "\n\n".join(page_texts).strip()
            page_count = len(doc)
            doc_metadata = doc.metadata or {}

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                f"Successfully extracted PDF '{filename}' ({page_count} pages, {len(extracted_text)} chars) in {elapsed_ms:.1f}ms"
            )

            return NormalizedDocument(
                filename=filename,
                document_type="pdf",
                extracted_text=extracted_text,
                page_count=page_count,
                extraction_time_ms=round(elapsed_ms, 2),
                metadata={
                    "file_size_bytes": file_size,
                    "title": doc_metadata.get("title"),
                    "author": doc_metadata.get("author"),
                    "creator": doc_metadata.get("creator"),
                    "producer": doc_metadata.get("producer"),
                    "creation_date": doc_metadata.get("creationDate"),
                },
            )

        except Exception as exc:
            logger.error(f"Error extracting PDF '{filename}': {exc}")
            raise
        finally:
            if doc is not None:
                doc.close()
