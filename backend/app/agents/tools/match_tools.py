"""
Deterministic Match Analysis tools for CrewAI MatchAnalyzerAgent.
Enables invoking the Phase 2 matching engine and querying evidence verification statuses.
Zero direct filesystem access or Git repository manipulation.
"""

import json
from typing import List, Any, Dict
from app.services.matching_engine import matching_engine
from app.services.evidence_service import evidence_service
from app.schemas.intelligence import ResumeProfile, JobProfile
from app.db.session import SessionLocal
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


def calculate_baseline_match_fn(resume_data_json: str, jd_data_json: str) -> str:
    """
    Invoke the deterministic Phase 2 matching engine to calculate explainable match scores
    across all 7 weighted dimensions.
    Returns JSON with overall score, dimension scores, matched, partial, and missing requirements.
    """
    try:
        resume_dict = json.loads(resume_data_json) if isinstance(resume_data_json, str) else resume_data_json
        jd_dict = json.loads(jd_data_json) if isinstance(jd_data_json, str) else jd_data_json

        resume_profile = ResumeProfile.model_validate(resume_dict)
        job_profile = JobProfile.model_validate(jd_dict)

        result = matching_engine.compute_match(resume_profile, job_profile)
        classification = "STRONG_MATCH" if result.overall_score >= 80 else ("MODERATE_MATCH" if result.overall_score >= 60 else "WEAK_MATCH")
        return json.dumps({
            "overall_score": result.overall_score,
            "classification": classification,
            "dimension_scores": result.dimension_scores.model_dump(),
            "matched_requirements_count": len(result.matched_requirements),
            "partial_requirements_count": len(result.partial_matches),
            "missing_requirements_count": len(result.missing_requirements),
            "explanation": result.summary_explanation,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error calculating baseline match score: {e}")
        return json.dumps({"error": str(e)})


def retrieve_skill_evidence_fn(skill: str) -> str:
    """
    Check the local SQLite database for verified repository evidence supporting a specific skill.
    Returns JSON with verification status (VERIFIED, LIKELY, WEAK, UNVERIFIED) and evidence count.
    """
    db = SessionLocal()
    try:
        res = evidence_service.verify_skill(skill, db)
        return json.dumps({
            "skill": res.skill,
            "canonical_skill": res.canonical_skill,
            "status": res.status,
            "confidence": res.confidence,
            "evidence_count": res.evidence_count,
            "summary": res.summary,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error retrieving skill evidence for '{skill}': {e}")
        return json.dumps({"error": str(e), "skill": skill})
    finally:
        db.close()


# CrewAI Tool Decorators
@tool("calculate_baseline_match")
def calculate_baseline_match_tool(resume_data_json: str, jd_data_json: str) -> str:
    """Calculate deterministic baseline match score and 7-dimension breakdown."""
    return calculate_baseline_match_fn(resume_data_json, jd_data_json)


@tool("retrieve_skill_evidence")
def retrieve_skill_evidence_tool(skill: str) -> str:
    """Query evidence verification level for a specific skill from registered projects."""
    return retrieve_skill_evidence_fn(skill)


def get_match_tools() -> List[Any]:
    """Return all deterministic tools permitted for MatchAnalyzerAgent."""
    return [
        calculate_baseline_match_tool,
        retrieve_skill_evidence_tool,
    ]
