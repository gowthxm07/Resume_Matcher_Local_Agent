"""
Document ingestion endpoints for PDF, DOCX, TXT, and Markdown files.
Enforces strict type validation, file size limits, filename sanitization, and PII protection.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.parser import DocumentParser, sanitize_filename, SecurityError
from app.schemas.ingestion import IngestionResponse, NormalizedDocument
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.post("/ingest/extract", response_model=IngestionResponse, tags=["Document Ingestion"])
async def extract_document(file: UploadFile = File(...)) -> IngestionResponse:
    """
    Extract text and metadata from an uploaded document (PDF, DOCX, TXT, MD).
    Validates file extension, sanitizes filename, and ensures zero cloud leakage.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing filename")

    safe_name = sanitize_filename(file.filename)

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes)")

        if len(content) > settings.UPLOAD_MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size of {settings.UPLOAD_MAX_BYTES} bytes",
            )

        doc = DocumentParser.parse_bytes(content, safe_name)

        return IngestionResponse(
            success=True,
            document=NormalizedDocument(
                document_id=doc.document_id,
                filename=doc.filename,
                document_type=doc.document_type,
                extracted_text=doc.extracted_text,
                character_count=doc.character_count,
                word_count=doc.word_count,
                page_count=doc.page_count,
                metadata=doc.metadata,
                extraction_time_ms=doc.extraction_time_ms,
            ),
            error=None,
        )

    except SecurityError as sec_err:
        raise HTTPException(status_code=400, detail=str(sec_err))
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        logger.error(f"Failed to process document {safe_name}: {exc}")
        return IngestionResponse(
            success=False,
            document=None,
            error=f"Document extraction error: {str(exc)}",
        )
