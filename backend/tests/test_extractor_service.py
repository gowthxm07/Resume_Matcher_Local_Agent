"""
Unit tests for structured ResumeProfile and JobProfile extraction.
Verifies JSON parsing, fallback heuristics, content hash caching, and resilient error handling.
"""

import pytest
from unittest.mock import patch, AsyncMock
from app.services.extractor_service import (
    ExtractorService,
    extract_json_from_llm_response,
    compute_sha256,
)
from app.schemas.intelligence import ResumeProfile, JobProfile


def test_compute_sha256_deterministic():
    """Verify hash computation is consistent."""
    h1 = compute_sha256("Python developer resume")
    h2 = compute_sha256("Python developer resume")
    assert h1 == h2
    assert len(h1) == 64


def test_extract_json_from_markdown_fence():
    """Verify JSON extractor correctly peels markdown code fences."""
    fenced = """Here is the extracted resume data:
```json
{
  "candidate_name": "John Doe",
  "skills": {
    "programming_languages": ["Python", "Rust"]
  }
}
```
Hope this helps!"""
    parsed = extract_json_from_llm_response(fenced)
    assert parsed is not None
    assert parsed["candidate_name"] == "John Doe"
    assert "Rust" in parsed["skills"]["programming_languages"]


def test_extract_json_with_trailing_commas():
    """Verify JSON extractor repairs trailing commas in arrays/objects."""
    malformed = """{
      "candidate_name": "Jane Doe",
      "skills": {
        "programming_languages": ["Python", "Go", ],
      },
    }"""
    parsed = extract_json_from_llm_response(malformed)
    assert parsed is not None
    assert parsed["candidate_name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_deterministic_resume_extraction_fallback():
    """Verify deterministic fallback extracts skills and contacts without LLM."""
    service = ExtractorService()
    raw_resume = """Alex Turner
alex.turner@example.com | (555) 234-5678 | github.com/alexturner
Senior Software Engineer with 5 years experience in Python, FastAPI, and PostgreSQL.
B.S. in Computer Science, State University.
Projects:
Built a distributed caching proxy in Python and Redis."""

    with patch.object(service, "_extract_resume_llm", new=AsyncMock(return_value=None)):
        profile = await service.extract_resume(raw_resume, force_refresh=True)
    assert isinstance(profile, ResumeProfile)
    assert profile.contact_info.email == "alex.turner@example.com"
    assert "github.com/alexturner" in (profile.contact_info.github_url or "")
    assert "Python" in profile.skills.programming_languages
    assert "FastAPI" in profile.skills.frameworks
    assert "PostgreSQL" in profile.skills.databases


@pytest.mark.asyncio
async def test_resume_caching():
    """Verify identical resume text hits cache without re-extracting."""
    service = ExtractorService()
    text = "Jane Candidate\njane@example.com\nPython, Docker"

    with patch.object(service, "_extract_resume_llm", new=AsyncMock(return_value=None)):
        p1 = await service.extract_resume(text)
        p2 = await service.extract_resume(text)
    assert p1.raw_text_hash == p2.raw_text_hash
    assert p1 is p2  # Same object reference from cache


@pytest.mark.asyncio
async def test_deterministic_jd_extraction_fallback():
    """Verify deterministic JD extractor separates required and preferred skills."""
    service = ExtractorService()
    raw_jd = """Senior Backend Engineer
Required Qualifications:
- Proficiency in Python and PostgreSQL
- Strong experience with FastAPI

Nice to have / Preferred:
- Experience with Docker and AWS
5+ years of experience required."""

    with patch.object(service, "_extract_jd_llm", new=AsyncMock(return_value=None)):
        profile = await service.extract_job_description(raw_jd, force_refresh=True)
    assert isinstance(profile, JobProfile)
    assert "Python" in profile.required_skills
    assert "Docker" in profile.preferred_skills
    assert profile.min_years_experience == 5.0
