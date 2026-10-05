"""
Unit tests for document ingestion and text extraction (PDF, DOCX, TXT, MD).
Tests include valid document parsing, invalid file handling, and security sanitization.
"""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import pymupdf as fitz
import docx
from app.ingestion.parser import DocumentParser, sanitize_filename, SecurityError
from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.docx_extractor import DOCXExtractor
from app.ingestion.text_extractor import TextExtractor


def create_sample_pdf_bytes(text: str = "Candidate Profile: Senior Backend Engineer") -> bytes:
    """Helper to generate a real, valid in-memory PDF document using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_sample_docx_bytes(paragraphs: list = None) -> bytes:
    """Helper to generate a valid in-memory DOCX document using python-docx."""
    if paragraphs is None:
        paragraphs = ["Candidate Experience", "Led development of distributed local AI systems."]
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc_io = io.BytesIO()
    doc.save(doc_io)
    return doc_io.getvalue()


def test_filename_sanitization():
    """Verify filename sanitization eliminates path traversal and unsafe characters."""
    assert sanitize_filename("../../../etc/shadow.pdf") == "shadow.pdf"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe.docx") == "cmd.exe.docx"
    assert sanitize_filename("resume\x00_test.pdf") == "resume_test.pdf"
    assert sanitize_filename("my resume (1).pdf") == "my resume _1_.pdf"


def test_pdf_extraction():
    """Verify PDF extraction extracts text and page count via PyMuPDF."""
    pdf_bytes = create_sample_pdf_bytes("Alice Smith - Python and FastAPI Expert")
    doc = PDFExtractor.extract(pdf_bytes, "alice_resume.pdf")

    assert doc.document_type == "pdf"
    assert doc.page_count == 1
    assert "Alice Smith" in doc.extracted_text
    assert "FastAPI Expert" in doc.extracted_text
    assert doc.character_count > 0


def test_docx_extraction():
    """Verify DOCX extraction extracts paragraphs via python-docx."""
    docx_bytes = create_sample_docx_bytes(["Bob Jones", "5 years experience in machine learning."])
    doc = DOCXExtractor.extract(docx_bytes, "bob_resume.docx")

    assert doc.document_type == "docx"
    assert "Bob Jones" in doc.extracted_text
    assert "machine learning" in doc.extracted_text


def test_text_and_markdown_extraction():
    """Verify TXT and Markdown extraction."""
    txt_content = b"Candidate: Carol Danvers\nSkills: Distributed systems, Go, Python"
    txt_doc = TextExtractor.extract(txt_content, "carol.txt", doc_type="txt")
    assert "Carol Danvers" in txt_doc.extracted_text
    assert txt_doc.document_type == "txt"

    md_content = b"# Job Description: AI Architect\n\nRequirements:\n- 10+ years experience"
    md_doc = TextExtractor.extract(md_content, "jd.md", doc_type="md")
    assert "Job Description: AI Architect" in md_doc.extracted_text
    assert md_doc.document_type == "md"


def test_reject_unsupported_file_extension():
    """Verify parser rejects executable or unsupported file extensions."""
    with pytest.raises(ValueError) as exc:
        DocumentParser.parse_bytes(b"binary payload", "malicious_script.exe")
    assert "Unsupported file extension" in str(exc.value)


def test_reject_oversized_file():
    """Verify parser enforces maximum file size limit."""
    oversized = b"A" * (11 * 1024 * 1024)  # 11MB exceeds 10MB limit
    with pytest.raises(SecurityError) as exc:
        DocumentParser.parse_bytes(oversized, "huge_resume.pdf")
    assert "exceeds maximum allowed" in str(exc.value)


def test_ingest_api_endpoint(client: TestClient):
    """Verify POST /api/ingest/extract with a real PDF upload."""
    pdf_bytes = create_sample_pdf_bytes("David Miller - Systems Engineer")
    files = {"file": ("david_resume.pdf", pdf_bytes, "application/pdf")}

    response = client.post("/api/ingest/extract", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["document"] is not None
    assert "David Miller" in data["document"]["extracted_text"]
    assert data["document"]["document_type"] == "pdf"


def test_ingest_api_invalid_extension(client: TestClient):
    """Verify POST /api/ingest/extract rejects invalid extensions with 400."""
    files = {"file": ("script.sh", b"echo hello", "text/x-sh")}
    response = client.post("/api/ingest/extract", files=files)
    assert response.status_code == 400
