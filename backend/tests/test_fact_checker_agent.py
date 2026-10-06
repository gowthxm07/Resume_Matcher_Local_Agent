"""
Tests for FactCheckerAgent, atomic claim extraction, and strict evidence grounding verification.
Verifies rejection of unverified technologies, metrics, percentages, user counts, and achievements.
"""

import json
import pytest
from app.agents.fact_checker import FactCheckerAgent
from app.agents.base import AgentRole
from app.agents.tools import verify_agent_tool_permissions, get_tool_name
from app.services.fact_checker_service import FactCheckerService
from app.schemas.optimization import (
    OptimizationChange,
    FactCheckStatus,
    ClaimCategory,
    ChangeType,
)


def test_fact_checker_instantiation():
    """Verify FactCheckerAgent initializes with proper role, goal, and local configuration."""
    checker = FactCheckerAgent()
    assert checker.role == AgentRole.FACT_CHECKER.value
    assert "Strict Truth" in checker.name
    assert "rejecting any unverified or fabricated claim" in checker.goal
    assert checker.metadata.llm_model == "llama3.2:3b"


def test_fact_checker_tool_permissions():
    """Verify FactCheckerAgent has strictly permitted tools and zero arbitrary tools."""
    checker = FactCheckerAgent()
    tools = checker.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    expected_tools = {
        "retrieve_claim",
        "retrieve_evidence",
        "verify_skill",
        "compare_claim_evidence",
    }
    assert tool_names == expected_tools
    assert verify_agent_tool_permissions(checker.role, tools) is True
    assert "scan_git_repository" not in tool_names


def test_claim_extraction_from_statement():
    """Verify atomic extraction of technologies, metrics, and achievements from text."""
    text = "Built a React dashboard with PostgreSQL serving 50,000 users and reduced latency by 40%."
    claims = FactCheckerService.extract_claims_from_text(text)

    categories = {c.category for c in claims}
    texts = [c.text.lower() for c in claims]

    assert ClaimCategory.TECHNOLOGY.value in categories
    assert ClaimCategory.METRIC.value in categories

    assert any("react" in t for t in texts)
    assert any("postgresql" in t for t in texts)
    assert any("50,000 users" in t for t in texts)
    assert any("40%" in t for t in texts)


def test_supported_technology_change():
    """Verify supported technology is verified when matching registered project evidence."""
    change = OptimizationChange(
        change_id="c1",
        original_text="Built an AI receptionist.",
        proposed_text="Built a full-stack AI receptionist using Next.js, Express, and PostgreSQL.",
        reason="Add verified tech stack",
        change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
    )

    trusted_resume = "Built an AI receptionist."
    verified_techs = {"next.js", "express", "postgresql", "ollama"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status == FactCheckStatus.SUPPORTED.value
    assert len(result.unsupported_claims) == 0
    assert len(result.verified_claims) >= 3


def test_unsupported_technology_rejected():
    """Verify unverified technology (AWS) is rejected when absent from resume and repos."""
    change = OptimizationChange(
        change_id="c2",
        original_text="Built an AI receptionist.",
        proposed_text="Built an AI receptionist deployed on AWS with Kubernetes.",
        reason="Align with JD requirements",
        change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
    )

    trusted_resume = "Built an AI receptionist using Python and SQLite."
    verified_techs = {"python", "sqlite", "fastapi"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status == FactCheckStatus.UNSUPPORTED.value
    unsupp_texts = [c.text.lower() for c in result.unsupported_claims]
    assert any("aws" in t or "kubernetes" in t for t in unsupp_texts)


def test_unsupported_metric_rejected():
    """Verify fabricated quantitative metrics (50,000 users, 99.9% uptime) are rejected."""
    change = OptimizationChange(
        change_id="c3",
        original_text="Built an AI receptionist.",
        proposed_text="Built a scalable AI receptionist serving 50,000 users with 99.9% uptime.",
        reason="Add business impact metrics",
        change_type=ChangeType.ACHIEVEMENT_FRAMING.value,
    )

    trusted_resume = "Built an AI receptionist."
    verified_techs = {"next.js", "express", "postgresql"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status in (FactCheckStatus.UNSUPPORTED.value, FactCheckStatus.PARTIALLY_SUPPORTED.value)
    unsupp_texts = [c.text.lower() for c in result.unsupported_claims]
    assert any("50,000 users" in t for t in unsupp_texts)
    assert any("99.9%" in t for t in unsupp_texts)


def test_partially_supported_claim_repair():
    """Verify partially supported bullet attempts deterministic repair by stripping unverified metric."""
    change = OptimizationChange(
        change_id="c4",
        original_text="Built an AI receptionist.",
        proposed_text="Built a Next.js AI receptionist serving 50,000 users.",
        reason="Enhance tech and metric",
        change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
    )

    trusted_resume = "Built an AI receptionist."
    verified_techs = {"next.js"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status == FactCheckStatus.PARTIALLY_SUPPORTED.value
    assert result.repaired_text is not None
    assert "50,000 users" not in result.repaired_text
    assert "Next.js" in result.repaired_text


def test_zero_repository_safety_rejects_external_claims():
    """Verify that with zero repositories, new technologies cannot be accepted as verified."""
    change = OptimizationChange(
        change_id="c5",
        original_text="Software developer with experience in building web apps.",
        proposed_text="Software developer with deep Redis caching and Docker containerization experience.",
        reason="Add backend tools",
        change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
    )

    trusted_resume = "Software developer with experience in building web apps with HTML and CSS."
    # 0 registered repos -> empty verified techs
    verified_techs = set()

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status == FactCheckStatus.UNSUPPORTED.value
