"""
Deterministic ATS validation tools for CrewAI ATSValidatorAgent.
Simulates applicant tracking system parsers and computes objective compatibility metrics.
Zero unrestricted filesystem access.
"""

import json
from typing import List, Any
from app.services.ats_service import ATSService
from app.services.skill_normalizer import SkillNormalizer
from app.core.logging import logger

try:
    from crewai.tools import tool
except ImportError:
    def tool(name_or_func=None):
        if callable(name_or_func):
            return name_or_func
        def decorator(f):
            return f
        return decorator


def validate_resume_structure_fn(resume_text: str) -> str:
    """Analyze section headers and hierarchy structure of resume text."""
    score, identified, missing = ATSService._audit_sections(resume_text)
    return json.dumps({
        "section_structure_score": score,
        "identified_sections": identified,
        "missing_sections": missing,
    }, indent=2)


def calculate_keyword_coverage_fn(resume_text: str, jd_text: str) -> str:
    """Calculate overlap between job keywords and candidate resume."""
    jd_skills = SkillNormalizer.extract_and_normalize_skills(jd_text)
    req_skills = jd_skills[:8]
    score, matched, missing = ATSService._audit_skill_coverage(resume_text, req_skills)
    return json.dumps({
        "coverage_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }, indent=2)


def validate_parseability_fn(resume_text: str) -> str:
    """Assess whether resume text is clean, free of control codes and corrupted bytes."""
    score, hazards = ATSService._audit_parseability(resume_text)
    return json.dumps({
        "parseability_score": score,
        "hazards": hazards,
    }, indent=2)


def detect_keyword_stuffing_fn(resume_text: str) -> str:
    """Detect unnatural keyword repetition and density anomalies."""
    skills = SkillNormalizer.extract_and_normalize_skills(resume_text)
    stuffing, dist_score = ATSService._audit_keyword_distribution(resume_text, skills)
    return json.dumps({
        "distribution_score": dist_score,
        "detected_stuffing_keywords": stuffing,
        "has_stuffing": len(stuffing) > 0,
    }, indent=2)


def calculate_ats_score_fn(resume_text: str, jd_text: str) -> str:
    """Compute overall heuristic ATS compatibility score and diagnostic metrics."""
    res = ATSService.evaluate_resume(resume_text, job_description_text=jd_text)
    return json.dumps(res.model_dump(), indent=2)


@tool("validate_resume_structure")
def validate_resume_structure_tool(resume_text: str) -> str:
    """Analyze section headers and hierarchy structure of resume text."""
    return validate_resume_structure_fn(resume_text)


@tool("calculate_keyword_coverage")
def calculate_keyword_coverage_tool(resume_text: str, jd_text: str) -> str:
    """Calculate overlap between job keywords and candidate resume."""
    return calculate_keyword_coverage_fn(resume_text, jd_text)


@tool("validate_parseability")
def validate_parseability_tool(resume_text: str) -> str:
    """Assess whether resume text is clean, free of control codes and corrupted bytes."""
    return validate_parseability_fn(resume_text)


@tool("detect_keyword_stuffing")
def detect_keyword_stuffing_tool(resume_text: str) -> str:
    """Detect unnatural keyword repetition and density anomalies."""
    return detect_keyword_stuffing_fn(resume_text)


@tool("calculate_ats_score")
def calculate_ats_score_tool(resume_text: str, jd_text: str) -> str:
    """Compute overall heuristic ATS compatibility score and diagnostic metrics."""
    return calculate_ats_score_fn(resume_text, jd_text)


def get_ats_tools() -> List[Any]:
    """Return strictly permitted tools for ATSValidatorAgent."""
    return [
        validate_resume_structure_tool,
        calculate_keyword_coverage_tool,
        validate_parseability_tool,
        detect_keyword_stuffing_tool,
        calculate_ats_score_tool,
    ]
