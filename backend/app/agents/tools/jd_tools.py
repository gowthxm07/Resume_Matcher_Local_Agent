"""
Deterministic Job Description analysis tools for CrewAI JDAnalyzerAgent.
Restricted strictly to requirement classification, skill normalization, and experience parsing.
Zero access to git scanning, repository access, or matching score engine.
"""

import json
from typing import List, Any
from app.services.requirement_classifier import RequirementClassifier
from app.services.skill_normalizer import skill_normalizer
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


def classify_job_requirement_fn(requirement_text: str) -> str:
    """
    Classify a single job requirement into REQUIRED vs PREFERRED,
    categorize it (PROGRAMMING_LANGUAGE, DATABASE, CLOUD, etc.),
    and determine its importance weight (critical, high, medium, low).
    """
    try:
        req = RequirementClassifier.classify_requirement(requirement_text)
        return json.dumps({
            "canonical_skill": req.canonical_skill,
            "requirement_type": req.requirement_type.value,
            "category": req.category.value,
            "importance": req.importance,
            "min_years": req.min_years,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error classifying JD requirement: {e}")
        return json.dumps({"error": str(e), "text": requirement_text})


def normalize_jd_skill_fn(skill: str) -> str:
    """
    Normalize a skill string from a job description to its canonical taxonomy ID
    and return its skill category.
    """
    try:
        canonical = skill_normalizer.normalize(skill)
        category = skill_normalizer.get_category(skill)
        return json.dumps({
            "raw_skill": skill,
            "canonical_skill": canonical,
            "category": category.value if category else "other",
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error normalizing JD skill: {e}")
        return json.dumps({"error": str(e), "skill": skill})


def extract_experience_requirement_fn(requirement_text: str) -> str:
    """
    Parse minimum required professional experience in years from requirement text.
    """
    try:
        years = RequirementClassifier.extract_experience_years(requirement_text)
        return json.dumps({
            "text": requirement_text,
            "years": years,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error extracting experience years: {e}")
        return json.dumps({"error": str(e), "text": requirement_text})


# CrewAI Tool Decorators
@tool("classify_job_requirement")
def classify_job_requirement_tool(requirement_text: str) -> str:
    """Classify JD requirement into REQUIRED vs PREFERRED with category and weight."""
    return classify_job_requirement_fn(requirement_text)


@tool("normalize_jd_skill")
def normalize_jd_skill_tool(skill: str) -> str:
    """Normalize a skill mentioned in the job description to its canonical form."""
    return normalize_jd_skill_fn(skill)


@tool("extract_experience_requirement")
def extract_experience_requirement_tool(requirement_text: str) -> str:
    """Extract minimum years of required experience from requirement text."""
    return extract_experience_requirement_fn(requirement_text)


def get_jd_tools() -> List[Any]:
    """Return all deterministic tools permitted for JDAnalyzerAgent."""
    return [
        classify_job_requirement_tool,
        normalize_jd_skill_tool,
        extract_experience_requirement_tool,
    ]
