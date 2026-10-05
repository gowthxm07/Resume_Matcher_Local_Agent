"""
Tests for agent tool permissions and role-based tool boundary enforcement.
Verifies that each agent only has access to its authorized deterministic tools.
"""

import json
import pytest
from app.agents.jd_analyzer import JDAnalyzerAgent
from app.agents.resume_analyzer import ResumeAnalyzerAgent
from app.agents.evidence import EvidenceAgent
from app.agents.match_analyzer import MatchAnalyzerAgent
from app.agents.manager import ManagerAgent
from app.agents.tools import (
    verify_agent_tool_permissions,
    get_tool_name,
    ALLOWED_TOOL_NAMES,
)
from app.agents.tools.jd_tools import (
    classify_job_requirement_fn,
    normalize_jd_skill_fn,
    extract_experience_requirement_fn,
)
from app.agents.tools.resume_tools import (
    normalize_candidate_skill_fn,
    categorize_candidate_skill_fn,
)
from app.agents.tools.match_tools import (
    calculate_baseline_match_fn,
    retrieve_skill_evidence_fn,
)


def test_manager_has_zero_technical_tools():
    """Verify ManagerAgent has strictly zero direct technical execution tools."""
    manager = ManagerAgent()
    tools = manager.get_tools()
    assert len(tools) == 0
    assert verify_agent_tool_permissions(manager.role, tools) is True


def test_jd_analyzer_tool_permissions():
    """Verify JDAnalyzerAgent has only JD analysis tools and cannot access git scanner or match tools."""
    jd = JDAnalyzerAgent()
    tools = jd.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    assert tool_names == {
        "classify_job_requirement",
        "normalize_jd_skill",
        "extract_experience_requirement",
    }
    assert verify_agent_tool_permissions(jd.role, tools) is True

    # Security check: JD agent must NOT have git scanner or matching engine
    assert "scan_git_repository" not in tool_names
    assert "calculate_baseline_match" not in tool_names


def test_resume_analyzer_tool_permissions():
    """Verify ResumeAnalyzerAgent has only resume analysis tools and cannot access git scanner."""
    resume = ResumeAnalyzerAgent()
    tools = resume.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    assert tool_names == {
        "normalize_candidate_skill",
        "categorize_candidate_skill",
    }
    assert verify_agent_tool_permissions(resume.role, tools) is True

    # Security check: Resume agent must NOT have git scanner or modify tools
    assert "scan_git_repository" not in tool_names


def test_evidence_agent_tool_permissions():
    """Verify EvidenceAgent has strictly evidence inspection tools and cannot access JD tools."""
    evidence = EvidenceAgent()
    tools = evidence.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    assert tool_names == {
        "scan_git_repository",
        "extract_commit_evidence",
        "find_skill_evidence",
        "verify_skill",
    }
    assert verify_agent_tool_permissions(evidence.role, tools) is True
    assert "classify_job_requirement" not in tool_names


def test_match_analyzer_tool_permissions():
    """Verify MatchAnalyzerAgent has match and evidence retrieval tools, but zero direct git tools."""
    match = MatchAnalyzerAgent()
    tools = match.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    assert tool_names == {
        "calculate_baseline_match",
        "retrieve_skill_evidence",
    }
    assert verify_agent_tool_permissions(match.role, tools) is True
    assert "scan_git_repository" not in tool_names


def test_permission_boundary_violation_caught():
    """Verify verify_agent_tool_permissions detects unauthorized tool injection."""
    # Attempt to inject Git Scanner into JD Analyzer
    unauthorized_tools = [
        lambda: None,  # fake
    ]
    unauthorized_tools[0].name = "scan_git_repository"

    is_valid = verify_agent_tool_permissions("JD Analyzer Agent", unauthorized_tools)
    assert is_valid is False


def test_jd_tool_functions_execute_deterministically():
    """Verify deterministic execution of JD tools."""
    res_cls = json.loads(classify_job_requirement_fn("Must have 5+ years of Python"))
    assert res_cls["canonical_skill"] == "Python"
    assert res_cls["requirement_type"] == "required"
    assert res_cls["min_years"] == 5.0

    res_norm = json.loads(normalize_jd_skill_fn("Postgres"))
    assert res_norm["canonical_skill"] == "PostgreSQL"
    assert res_norm["category"] == "database"

    res_exp = json.loads(extract_experience_requirement_fn("3-5 years of experience"))
    assert res_exp["years"] == 3.0


def test_resume_tool_functions_execute_deterministically():
    """Verify deterministic execution of Resume tools."""
    res_norm = json.loads(normalize_candidate_skill_fn("k8s"))
    assert res_norm["canonical_skill"] == "Kubernetes"
    assert res_norm["category"] == "devops"

    res_cat = json.loads(categorize_candidate_skill_fn("FastAPI"))
    assert res_cat["category"] == "framework"


def test_match_tool_functions_execute_deterministically():
    """Verify deterministic execution of Match tools."""
    resume_json = json.dumps({
        "name": "Test Candidate",
        "skills": {"all_skills": ["Python", "FastAPI"]},
        "work_experience": [],
        "education": [],
        "projects": [],
        "total_experience_years": 3.0,
    })
    jd_json = json.dumps({
        "title": "Backend Dev",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "min_experience_years": 2.0,
        "responsibilities": [],
    })

    match_res = json.loads(calculate_baseline_match_fn(resume_json, jd_json))
    assert "overall_score" in match_res
    assert match_res["overall_score"] > 0
