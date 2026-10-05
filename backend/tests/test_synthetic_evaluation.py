"""
Evaluation test suite executing against the synthetic evaluation dataset fixtures.
Verifies ground-truth ranking and scoring relationships across strong, moderate, and poor matches.
"""

import pytest
from app.services.matching_engine import matching_engine
from app.fixtures.synthetic_eval_dataset import (
    JD_SENIOR_PYTHON,
    JD_EMBEDDED_CPP,
    CANDIDATE_STRONG_PYTHON,
    CANDIDATE_MODERATE_PYTHON,
    CANDIDATE_POOR_MATCH_REACT,
    CANDIDATE_MISSING_POSTGRES,
    CANDIDATE_MISSING_PREFERRED,
)


@pytest.mark.asyncio
async def test_strong_match_score_above_threshold():
    """Verify Candidate A (Alice) against Senior Python role scores >= 80%."""
    res = await matching_engine.analyze_match(CANDIDATE_STRONG_PYTHON, JD_SENIOR_PYTHON)
    assert res.overall_score >= 80.0
    assert res.dimension_scores.required_skill_score == 100.0
    assert len(res.missing_requirements) == 0


@pytest.mark.asyncio
async def test_poor_match_score_below_threshold():
    """Verify Candidate C (Charlie - React) against Senior Python role scores < 40%."""
    res = await matching_engine.analyze_match(CANDIDATE_POOR_MATCH_REACT, JD_SENIOR_PYTHON)
    assert res.overall_score < 40.0
    assert res.dimension_scores.required_skill_score == 0.0


@pytest.mark.asyncio
async def test_relative_ranking_consistency():
    """
    Verify fundamental ranking order:
    Score(Strong Match) > Score(Moderate Match) > Score(Poor Match)
    """
    strong_res = await matching_engine.analyze_match(CANDIDATE_STRONG_PYTHON, JD_SENIOR_PYTHON)
    mod_res = await matching_engine.analyze_match(CANDIDATE_MODERATE_PYTHON, JD_SENIOR_PYTHON)
    poor_res = await matching_engine.analyze_match(CANDIDATE_POOR_MATCH_REACT, JD_SENIOR_PYTHON)

    assert strong_res.overall_score > mod_res.overall_score
    assert mod_res.overall_score > poor_res.overall_score


@pytest.mark.asyncio
async def test_missing_required_skill_penalty():
    """Verify Candidate D (Dana) missing PostgreSQL is penalized in required_skill_score."""
    alice_res = await matching_engine.analyze_match(CANDIDATE_STRONG_PYTHON, JD_SENIOR_PYTHON)
    dana_res = await matching_engine.analyze_match(CANDIDATE_MISSING_POSTGRES, JD_SENIOR_PYTHON)

    assert dana_res.dimension_scores.required_skill_score < alice_res.dimension_scores.required_skill_score
    missing_names = [m.canonical_skill for m in dana_res.missing_requirements]
    assert "PostgreSQL" in missing_names


@pytest.mark.asyncio
async def test_missing_preferred_vs_required_distinction():
    """
    Verify Candidate E (Edward) has 100% required skill coverage,
    but lower preferred skill coverage than Alice who has Docker and AWS.
    """
    alice_res = await matching_engine.analyze_match(CANDIDATE_STRONG_PYTHON, JD_SENIOR_PYTHON)
    edward_res = await matching_engine.analyze_match(CANDIDATE_MISSING_PREFERRED, JD_SENIOR_PYTHON)

    # Edward has all required: Python, FastAPI, PostgreSQL, REST API
    assert edward_res.dimension_scores.required_skill_score == 100.0
    # But lacks preferred Docker, AWS, Redis
    assert edward_res.dimension_scores.preferred_skill_score < alice_res.dimension_scores.preferred_skill_score
    assert edward_res.overall_score < alice_res.overall_score
