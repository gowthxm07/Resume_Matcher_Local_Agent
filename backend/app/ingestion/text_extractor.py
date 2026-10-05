"""
Plain text and Markdown extractor module with automatic encoding detection fallback.
"""

import time
from pathlib import Path
from typing import Union
from app.ingestion.document import NormalizedDocument
from app.core.logging import logger


class TextExtractor:
    """Extracts text content from .txt and .md files."""

    SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    @classmethod
    def extract(
        cls,
        file_path_or_bytes: Union[str, Path, bytes],
        filename: str,
        doc_type: str = "txt",
    ) -> NormalizedDocument:
        """
        Extract plain text or Markdown with encoding fallbacks.
        """
        start_time = time.perf_counter()
        try:
            if isinstance(file_path_or_bytes, (str, Path)):
                path = Path(file_path_or_bytes)
                if not path.exists():
                    raise FileNotFoundError(f"File not found at: {path}")
                raw_bytes = path.read_bytes()
            else:
                raw_bytes = file_path_or_bytes

            file_size = len(raw_bytes)
            extracted_text = ""
            detected_encoding = None

            for enc in cls.SUPPORTED_ENCODINGS:
                try:
                    extracted_text = raw_bytes.decode(enc).strip()
                    detected_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue

            if detected_encoding is None:
                # Ultimate fallback
                extracted_text = raw_bytes.decode("utf-8", errors="replace").strip()
                detected_encoding = "utf-8-replace"

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                f"Successfully extracted {doc_type.upper()} '{filename}' ({len(extracted_text)} chars) in {elapsed_ms:.1f}ms"
            )

            return NormalizedDocument(
                filename=filename,
                document_type=doc_type.lower(),
                extracted_text=extracted_text,
                page_count=None,
                extraction_time_ms=round(elapsed_ms, 2),
                metadata={
                    "file_size_bytes": file_size,
                    "encoding": detected_encoding,
                },
            )

        except Exception as exc:
            logger.error(f"Error extracting text file '{filename}': {exc}")
            raise
