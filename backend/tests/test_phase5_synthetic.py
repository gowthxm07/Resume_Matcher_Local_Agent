"""
Deterministic synthetic evaluation for Phase 5.
Demonstrates:
Scenario A: Valid optimization grounded in candidate repository evidence (SUPPORTED).
Scenario B: Hallucination rejection of fabricated metrics / user counts (REJECTED / UNSUPPORTED).
Scenario C: Anti-score-gaming verification — missing required skill (AWS) without evidence is NOT added.
"""

import pytest
from app.services.fact_checker_service import FactCheckerService
from app.schemas.optimization import (
    OptimizationChange,
    FactCheckStatus,
    ChangeType,
)


def test_scenario_a_valid_optimization_supported():
    """
    Scenario A: Valid Optimization
    Original: Built an AI receptionist.
    Evidence: Next.js, Express, PostgreSQL, Ollama
    Safe proposal: Built a full-stack AI receptionist platform using Next.js, Express, PostgreSQL and local Ollama inference.
    Result: SUPPORTED
    """
    original = "Built an AI receptionist."
    proposed = "Built a full-stack AI receptionist platform using Next.js, Express, PostgreSQL and local Ollama inference."

    change = OptimizationChange(
        change_id="demo_scenario_a",
        section="Experience",
        original_text=original,
        proposed_text=proposed,
        reason="Enrich with verified full-stack project technologies",
        change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
    )

    trusted_resume = "Built an AI receptionist."
    verified_techs = {"next.js", "express", "postgresql", "ollama", "ai receptionist"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status == FactCheckStatus.SUPPORTED.value
    assert len(result.unsupported_claims) == 0
    assert len(result.verified_claims) >= 4


def test_scenario_b_hallucination_metric_rejected():
    """
    Scenario B: Hallucination Rejection
    Proposed: Reduced AI response latency by 80% serving 50,000 users.
    No evidence exists for the metric.
    Result: REJECTED / UNSUPPORTED
    """
    original = "Built an AI receptionist."
    proposed = "Built an AI receptionist that reduced AI response latency by 80% serving 50,000 users."

    change = OptimizationChange(
        change_id="demo_scenario_b",
        section="Experience",
        original_text=original,
        proposed_text=proposed,
        reason="Claim massive performance and scale metrics to boost score",
        change_type=ChangeType.ACHIEVEMENT_FRAMING.value,
    )

    trusted_resume = "Built an AI receptionist."
    verified_techs = {"next.js", "express", "postgresql", "ollama"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    # Must be marked UNSUPPORTED or PARTIALLY_SUPPORTED with rejected metric claims
    assert result.overall_status in (FactCheckStatus.UNSUPPORTED.value, FactCheckStatus.PARTIALLY_SUPPORTED.value)
    unsupp_claims = [c.text.lower() for c in result.unsupported_claims]
    assert any("80%" in c or "latency" in c for c in unsupp_claims)
    assert any("50,000 users" in c for c in unsupp_claims)


def test_scenario_c_anti_score_gaming_rejects_missing_critical_skill():
    """
    Scenario C: Anti-Score Gaming
    JD requires: Python, Docker, PostgreSQL, AWS
    Candidate evidence proves: Python, Docker, PostgreSQL (NO AWS evidence)
    Attempting to add AWS simply to increase the score MUST BE REJECTED.
    """
    original = "Backend developer working with Python, Docker, and PostgreSQL."
    proposed = "Backend developer working with Python, Docker, PostgreSQL, and AWS cloud deployments."

    change = OptimizationChange(
        change_id="demo_scenario_c_gaming",
        section="Experience",
        original_text=original,
        proposed_text=proposed,
        reason="Inject AWS to increase JD required skills match score",
        change_type=ChangeType.KEYWORD_ALIGNMENT.value,
    )

    trusted_resume = "Backend developer working with Python, Docker, and PostgreSQL."
    # Verified repository technologies do NOT include AWS
    verified_techs = {"python", "docker", "postgresql"}

    result = FactCheckerService.verify_change(
        change=change,
        trusted_resume_text=trusted_resume,
        verified_technologies=verified_techs,
    )

    assert result.overall_status == FactCheckStatus.UNSUPPORTED.value
    unsupp_texts = [c.text.lower() for c in result.unsupported_claims]
    assert any("aws" in t for t in unsupp_texts)
