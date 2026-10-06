"""
Deterministic optimization tools for CrewAI ResumeOptimizerAgent.
Enables retrieving match gap analysis, extracting resume claims, and formatting structured proposals.
Zero unrestricted filesystem access or arbitrary execution capabilities.
"""

import json
import uuid
from typing import List, Any
from app.db.session import SessionLocal
from app.models.analysis_run import AnalysisRun
from app.models.resume import Resume
from app.services.evidence_service import evidence_service
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


def retrieve_match_analysis_fn(analysis_id: str) -> str:
    """Retrieve stored match analysis gaps and dimension scores."""
    db = SessionLocal()
    try:
        run = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
        if not run:
            return json.dumps({"error": f"Analysis run '{analysis_id}' not found."})
        return json.dumps({
            "analysis_id": run.id,
            "match_score": run.match_score,
            "evidence_confidence": run.evidence_confidence,
            "results_summary": run.results_summary or {},
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error retrieving match analysis: {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()


def retrieve_resume_claims_fn(resume_id: str) -> str:
    """Retrieve technical skills and bullet claims present in candidate's resume."""
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return json.dumps({"error": f"Resume '{resume_id}' not found."})
        skills = SkillNormalizer.extract_and_normalize_skills(resume.raw_text)
        return json.dumps({
            "resume_id": resume.id,
            "extracted_skills": skills,
            "text_length": len(resume.raw_text),
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error retrieving resume claims: {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()


def retrieve_skill_evidence_fn(skill_name: str) -> str:
    """Check repository verification evidence for a specific skill."""
    db = SessionLocal()
    try:
        res = evidence_service.verify_skill(skill_name, db)
        return json.dumps({
            "skill": res.skill,
            "status": res.status,
            "confidence": res.confidence,
            "evidence_count": res.evidence_count,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error querying skill evidence: {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()


def generate_optimization_proposal_fn(
    original_text: str,
    section: str,
    reason: str,
    change_type: str,
    proposed_text: str,
) -> str:
    """Format a proposed change into a structured optimization proposal payload."""
    proposal = {
        "change_id": f"chg_{uuid.uuid4().hex[:8]}",
        "section": section,
        "original_text": original_text,
        "proposed_text": proposed_text,
        "reason": reason,
        "change_type": change_type,
        "status": "PENDING",
    }
    return json.dumps(proposal, indent=2)


@tool("retrieve_match_analysis")
def retrieve_match_analysis_tool(analysis_id: str) -> str:
    """Retrieve stored match analysis gaps and dimension scores."""
    return retrieve_match_analysis_fn(analysis_id)


@tool("retrieve_resume_claims")
def retrieve_resume_claims_tool(resume_id: str) -> str:
    """Retrieve technical skills and bullet claims present in candidate's resume."""
    return retrieve_resume_claims_fn(resume_id)


@tool("retrieve_skill_evidence")
def retrieve_skill_evidence_tool(skill_name: str) -> str:
    """Check repository verification evidence for a specific skill."""
    return retrieve_skill_evidence_fn(skill_name)


@tool("generate_optimization_proposal")
def generate_optimization_proposal_tool(
    original_text: str,
    section: str,
    reason: str,
    change_type: str,
    proposed_text: str,
) -> str:
    """Format a proposed change into a structured optimization proposal payload."""
    return generate_optimization_proposal_fn(
        original_text, section, reason, change_type, proposed_text
    )


def get_optimizer_tools() -> List[Any]:
    """Return strictly permitted tools for ResumeOptimizerAgent."""
    return [
        retrieve_match_analysis_tool,
        retrieve_resume_claims_tool,
        retrieve_skill_evidence_tool,
        generate_optimization_proposal_tool,
    ]
