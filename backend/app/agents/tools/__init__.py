"""
Agent tools package for CareerCrew.
Deterministic tools used by specialized CrewAI agents with strict role-based tool boundary enforcement.
"""

from typing import List, Any
from app.agents.tools.evidence_tools import (
    scan_git_repository_tool,
    extract_commit_evidence_tool,
    find_skill_evidence_tool,
    verify_skill_tool,
    get_evidence_tools,
)
from app.agents.tools.jd_tools import (
    classify_job_requirement_tool,
    normalize_jd_skill_tool,
    extract_experience_requirement_tool,
    get_jd_tools,
)
from app.agents.tools.resume_tools import (
    normalize_candidate_skill_tool,
    categorize_candidate_skill_tool,
    get_resume_tools,
)
from app.agents.tools.match_tools import (
    calculate_baseline_match_tool,
    retrieve_skill_evidence_tool,
    get_match_tools,
)
from app.agents.tools.optimizer_tools import (
    retrieve_match_analysis_tool,
    retrieve_resume_claims_tool,
    generate_optimization_proposal_tool,
    get_optimizer_tools,
)
from app.agents.tools.fact_checker_tools import (
    retrieve_claim_tool,
    retrieve_evidence_tool,
    compare_claim_evidence_tool,
    get_fact_checker_tools,
)
from app.agents.tools.ats_tools import (
    validate_resume_structure_tool,
    calculate_keyword_coverage_tool,
    validate_parseability_tool,
    detect_keyword_stuffing_tool,
    calculate_ats_score_tool,
    get_ats_tools,
)

# Tool permissions boundary map
ALLOWED_TOOL_NAMES = {
    "JD Analyzer Agent": {
        "classify_job_requirement",
        "normalize_jd_skill",
        "extract_experience_requirement",
    },
    "Resume Analyzer Agent": {
        "normalize_candidate_skill",
        "categorize_candidate_skill",
    },
    "Evidence Agent": {
        "scan_git_repository",
        "extract_commit_evidence",
        "find_skill_evidence",
        "verify_skill",
    },
    "Match Analyzer Agent": {
        "calculate_baseline_match",
        "retrieve_skill_evidence",
    },
    "Manager Agent": set(),  # Manager agent has zero technical tools (orchestration only)
    "Resume Optimizer Agent": {
        "retrieve_match_analysis",
        "retrieve_resume_claims",
        "retrieve_skill_evidence",
        "generate_optimization_proposal",
    },
    "Impact-Driven Resume Optimizer": {
        "retrieve_match_analysis",
        "retrieve_resume_claims",
        "retrieve_skill_evidence",
        "generate_optimization_proposal",
    },
    "Fact Checker Agent": {
        "retrieve_claim",
        "retrieve_evidence",
        "verify_skill",
        "compare_claim_evidence",
    },
    "Strict Truth & Hallucination Auditor": {
        "retrieve_claim",
        "retrieve_evidence",
        "verify_skill",
        "compare_claim_evidence",
    },
    "ATS Validator Agent": {
        "validate_resume_structure",
        "calculate_keyword_coverage",
        "validate_parseability",
        "detect_keyword_stuffing",
        "calculate_ats_score",
    },
    "Applicant Tracking System Emulator": {
        "validate_resume_structure",
        "calculate_keyword_coverage",
        "validate_parseability",
        "detect_keyword_stuffing",
        "calculate_ats_score",
    },
    "Interview Agent": set(),
}


def get_tool_name(tool_obj: Any) -> str:
    """Extract tool name from CrewAI tool or callable."""
    if hasattr(tool_obj, "name"):
        return str(tool_obj.name)
    if hasattr(tool_obj, "__name__"):
        return str(tool_obj.__name__)
    return str(tool_obj)


def verify_agent_tool_permissions(agent_role_or_name: str, tools: List[Any]) -> bool:
    """
    Validate that an agent's assigned tools strictly comply with its architectural boundary.
    Returns True if compliant, False otherwise.
    """
    allowed_names = ALLOWED_TOOL_NAMES.get(agent_role_or_name, set())
    for t in tools:
        t_name = get_tool_name(t)
        if t_name not in allowed_names:
            return False
    return True


__all__ = [
    "scan_git_repository_tool",
    "extract_commit_evidence_tool",
    "find_skill_evidence_tool",
    "verify_skill_tool",
    "get_evidence_tools",
    "classify_job_requirement_tool",
    "normalize_jd_skill_tool",
    "extract_experience_requirement_tool",
    "get_jd_tools",
    "normalize_candidate_skill_tool",
    "categorize_candidate_skill_tool",
    "get_resume_tools",
    "calculate_baseline_match_tool",
    "retrieve_skill_evidence_tool",
    "get_match_tools",
    "retrieve_match_analysis_tool",
    "retrieve_resume_claims_tool",
    "generate_optimization_proposal_tool",
    "get_optimizer_tools",
    "retrieve_claim_tool",
    "retrieve_evidence_tool",
    "compare_claim_evidence_tool",
    "get_fact_checker_tools",
    "validate_resume_structure_tool",
    "calculate_keyword_coverage_tool",
    "validate_parseability_tool",
    "detect_keyword_stuffing_tool",
    "calculate_ats_score_tool",
    "get_ats_tools",
    "ALLOWED_TOOL_NAMES",
    "verify_agent_tool_permissions",
    "get_tool_name",
]
