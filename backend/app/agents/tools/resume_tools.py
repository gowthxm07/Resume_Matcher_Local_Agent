"""
Deterministic Resume analysis tools for CrewAI ResumeAnalyzerAgent.
Restricted strictly to candidate skill normalization, categorization, and taxonomy lookup.
Zero access to git scanning, repository access, or matching score engine.
"""

import json
from typing import List, Any
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


def normalize_candidate_skill_fn(skill: str) -> str:
    """
    Normalize a skill claimed on the candidate's resume to its canonical form
    and return its taxonomy category.
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
        logger.warning(f"Error normalizing candidate skill: {e}")
        return json.dumps({"error": str(e), "skill": skill})


def categorize_candidate_skill_fn(skill: str) -> str:
    """
    Lookup taxonomy category for a technical skill (e.g. PROGRAMMING_LANGUAGE, DATABASE).
    """
    try:
        cat = skill_normalizer.get_category(skill)
        return json.dumps({
            "skill": skill,
            "category": cat.value if cat else "other",
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error categorizing candidate skill: {e}")
        return json.dumps({"error": str(e), "skill": skill})


# CrewAI Tool Decorators
@tool("normalize_candidate_skill")
def normalize_candidate_skill_tool(skill: str) -> str:
    """Normalize a skill claimed on the resume to its canonical form."""
    return normalize_candidate_skill_fn(skill)


@tool("categorize_candidate_skill")
def categorize_candidate_skill_tool(skill: str) -> str:
    """Determine the technical category of a candidate-claimed skill."""
    return categorize_candidate_skill_fn(skill)


def get_resume_tools() -> List[Any]:
    """Return all deterministic tools permitted for ResumeAnalyzerAgent."""
    return [
        normalize_candidate_skill_tool,
        categorize_candidate_skill_tool,
    ]
