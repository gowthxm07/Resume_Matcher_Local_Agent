"""
Tests for ATSValidatorAgent, deterministic parser auditing, keyword stuffing detection, and ATS score heuristics.
"""

import pytest
from app.agents.ats_validator import ATSValidatorAgent
from app.agents.base import AgentRole
from app.agents.tools import verify_agent_tool_permissions, get_tool_name
from app.services.ats_service import ATSService, DISCLAIMER_TEXT
from app.schemas.optimization import ATSValidationResult


def test_ats_validator_instantiation():
    """Verify ATSValidatorAgent initializes with proper role, goal, and local configuration."""
    validator = ATSValidatorAgent()
    assert validator.role == AgentRole.ATS_VALIDATOR.value
    assert "Applicant Tracking System Emulator" in validator.name
    assert "optimal machine parseability" in validator.goal
    assert validator.metadata.llm_model == "llama3.2:3b"


def test_ats_validator_tool_permissions():
    """Verify ATSValidatorAgent has strictly permitted tools and zero arbitrary tools."""
    validator = ATSValidatorAgent()
    tools = validator.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    expected_tools = {
        "validate_resume_structure",
        "calculate_keyword_coverage",
        "validate_parseability",
        "detect_keyword_stuffing",
        "calculate_ats_score",
    }
    assert tool_names == expected_tools
    assert verify_agent_tool_permissions(validator.role, tools) is True


def test_ats_parseability_clean_vs_corrupted():
    """Verify clean resume text achieves high parseability, while corrupted text is flagged."""
    clean_text = (
        "PROFESSIONAL SUMMARY\nSoftware Engineer with 4 years of experience.\n\n"
        "EXPERIENCE\nBackend Developer at Acme Corp.\n- Built REST APIs in Python.\n"
        "- Optimized PostgreSQL queries.\n\n"
        "EDUCATION\nB.S. in Computer Science\n\n"
        "SKILLS\nPython, PostgreSQL, Docker\n"
    )
    score_clean, hazards_clean = ATSService._audit_parseability(clean_text)
    assert score_clean >= 90.0
    assert len(hazards_clean) == 0

    corrupted_text = "Corrupted\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b" * 10
    score_bad, hazards_bad = ATSService._audit_parseability(corrupted_text)
    assert score_bad < 70.0
    assert len(hazards_bad) > 0


def test_ats_section_structure_identification():
    """Verify detection of standard resume sections."""
    text = (
        "SUMMARY\nExperienced engineer.\n\n"
        "WORK EXPERIENCE\nSenior Developer at Tech Co.\n\n"
        "EDUCATION\nUniversity of Science\n\n"
        "TECHNICAL SKILLS\nPython, Docker, React\n"
    )
    score, identified, missing = ATSService._audit_sections(text)
    assert score >= 80.0
    assert "Summary" in identified
    assert "Experience" in identified
    assert "Education" in identified
    assert "Skills" in identified


def test_ats_keyword_stuffing_detection():
    """Verify excessive repeated keywords are detected and penalized."""
    stuffed_text = (
        "Python Python Python Python developer who loves Python and writes Python code in Python every day. "
        "Python Python Python is the best Python programming language."
    )
    stuffing, dist_score = ATSService._audit_keyword_distribution(stuffed_text, ["Python"])
    assert "Python" in stuffing
    assert dist_score < 80.0


def test_ats_formatting_hazards():
    """Verify parser-hostile unbroken lines or symbol spam are detected."""
    hostile_text = (
        "Heading\n"
        + ("A" * 400) + "\n"
        + "||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        + "\n\n\n\n\n\n\n"
        + "End of text"
    )
    score, hazards = ATSService._audit_formatting(hostile_text)
    assert len(hazards) > 0
    assert score < 100.0


def test_ats_score_heuristic_and_disclaimer():
    """Verify composite ATS score computation includes the required disclaimer."""
    resume_text = (
        "SUMMARY\nBackend software developer.\n\n"
        "EXPERIENCE\nSoftware Engineer at Startup\n- Built microservices using Python and Docker.\n\n"
        "SKILLS\nPython, Docker, PostgreSQL\n\n"
        "EDUCATION\nB.S. Software Engineering\n"
    )
    required = ["Python", "Docker", "PostgreSQL"]
    preferred = ["Redis"]

    result = ATSService.evaluate_resume(resume_text, required_skills=required, preferred_skills=preferred)

    assert 0.0 <= result.overall_ats_score <= 100.0
    assert result.parseability_score > 0
    assert result.section_structure_score > 0
    assert result.required_skill_coverage_score == 100.0
    assert len(result.detected_stuffing_keywords) == 0
    assert DISCLAIMER_TEXT in result.disclaimer
    assert "heuristic estimates" in result.disclaimer
