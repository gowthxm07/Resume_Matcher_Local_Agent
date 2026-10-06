"""
Deterministic fact-checking tools for CrewAI FactCheckerAgent.
Enables retrieving atomic claims, querying repository evidence, verifying skills,
and comparing claims against evidence to prevent hallucinations.
Zero unrestricted filesystem access or write capabilities.
"""

import json
from typing import List, Any
from app.db.session import SessionLocal
from app.models.evidence_record import EvidenceRecord
from app.services.evidence_service import evidence_service
from app.services.fact_checker_service import FactCheckerService
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


def retrieve_claim_fn(claim_text: str) -> str:
    """Extract ontological entities and claims from candidate statement."""
    claims = FactCheckerService.extract_claims_from_text(claim_text)
    return json.dumps([c.model_dump() for c in claims], indent=2)


def retrieve_evidence_fn(skill_or_entity: str) -> str:
    """Retrieve raw EvidenceRecords matching a specific technology or entity."""
    db = SessionLocal()
    try:
        records = (
            db.query(EvidenceRecord)
            .filter(EvidenceRecord.skill_name.ilike(f"%{skill_or_entity}%"))
            .limit(5)
            .all()
        )
        data = [
            {
                "id": r.id,
                "skill_name": r.skill_name,
                "file_path": r.file_path,
                "evidence_type": r.evidence_type,
                "confidence_score": r.confidence_score,
                "source_snippet": r.source_snippet,
            }
            for r in records
        ]
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.warning(f"Error retrieving evidence for '{skill_or_entity}': {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()


def verify_skill_fn(skill_name: str) -> str:
    """Formally verify a skill against all candidate project repositories."""
    db = SessionLocal()
    try:
        res = evidence_service.verify_skill(skill_name, db)
        return json.dumps({
            "skill": res.skill,
            "status": res.status,
            "confidence": res.confidence,
            "evidence_count": res.evidence_count,
            "summary": res.summary,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error verifying skill '{skill_name}': {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()


def compare_claim_evidence_fn(claim_text: str, original_text: str) -> str:
    """Compare a proposed statement against the original statement and repository evidence."""
    db = SessionLocal()
    try:
        records = db.query(EvidenceRecord).all()
        from app.schemas.optimization import OptimizationChange
        change = OptimizationChange(
            change_id="temp",
            original_text=original_text,
            proposed_text=claim_text,
            reason="Ad-hoc comparison",
        )
        res = FactCheckerService.verify_change(
            change=change,
            trusted_resume_text=original_text,
            evidence_records=records,
        )
        return json.dumps({
            "overall_status": res.overall_status,
            "verified_claims_count": len(res.verified_claims),
            "unsupported_claims_count": len(res.unsupported_claims),
            "repaired_text": res.repaired_text,
            "notes": res.notes,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error comparing claim against evidence: {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()


@tool("retrieve_claim")
def retrieve_claim_tool(claim_text: str) -> str:
    """Extract ontological entities and claims from candidate statement."""
    return retrieve_claim_fn(claim_text)


@tool("retrieve_evidence")
def retrieve_evidence_tool(skill_or_entity: str) -> str:
    """Retrieve raw EvidenceRecords matching a specific technology or entity."""
    return retrieve_evidence_fn(skill_or_entity)


@tool("verify_skill")
def verify_skill_tool(skill_name: str) -> str:
    """Formally verify a skill against all candidate project repositories."""
    return verify_skill_fn(skill_name)


@tool("compare_claim_evidence")
def compare_claim_evidence_tool(claim_text: str, original_text: str) -> str:
    """Compare a proposed statement against the original statement and repository evidence."""
    return compare_claim_evidence_fn(claim_text, original_text)


def get_fact_checker_tools() -> List[Any]:
    """Return strictly permitted tools for FactCheckerAgent."""
    return [
        retrieve_claim_tool,
        retrieve_evidence_tool,
        verify_skill_tool,
        compare_claim_evidence_tool,
    ]
