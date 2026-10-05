"""
Synthetic evaluation comparing Baseline Matching Engine vs CrewAI Multi-Agent Dossier.
Verifies monotonic ranking consistency, score validity, and evidence grounding preservation.
"""

import pytest
from app.services.matching_engine import matching_engine
from app.services.crew_service import crew_service
from app.fixtures.synthetic_eval_dataset import (
    JD_SENIOR_PYTHON,
    CANDIDATE_STRONG_PYTHON,
    CANDIDATE_MODERATE_PYTHON,
    CANDIDATE_POOR_MATCH_REACT,
)


def test_synthetic_monotonic_ranking_preserved(db_session):
    """
    Verify ranking order across synthetic candidate profiles:
    Score(Alice: Strong) > Score(Bob: Moderate) > Score(Charlie: Poor).
    Both in Baseline matching engine and Crew multi-agent synthesis.
    """
    # 1. Baseline scores
    alice_base = matching_engine.compute_match(CANDIDATE_STRONG_PYTHON, JD_SENIOR_PYTHON)
    bob_base = matching_engine.compute_match(CANDIDATE_MODERATE_PYTHON, JD_SENIOR_PYTHON)
    charlie_base = matching_engine.compute_match(CANDIDATE_POOR_MATCH_REACT, JD_SENIOR_PYTHON)

    assert alice_base.overall_score > bob_base.overall_score
    assert bob_base.overall_score > charlie_base.overall_score

    # 2. Crew Dossier synthesis
    # Convert synthetic profiles into text representations
    alice_text = f"Skills: {', '.join(CANDIDATE_STRONG_PYTHON.skills.all_skills)}. Experience: {CANDIDATE_STRONG_PYTHON.total_experience_years} years."
    bob_text = f"Skills: {', '.join(CANDIDATE_MODERATE_PYTHON.skills.all_skills)}. Experience: {CANDIDATE_MODERATE_PYTHON.total_experience_years} years."
    charlie_text = f"Skills: {', '.join(CANDIDATE_POOR_MATCH_REACT.skills.all_skills)}. Experience: {CANDIDATE_POOR_MATCH_REACT.total_experience_years} years."
    jd_text = f"Title: {JD_SENIOR_PYTHON.title}. Requirements: {', '.join(JD_SENIOR_PYTHON.required_skills)}."

    alice_dossier = crew_service.run_analysis(raw_resume_text=alice_text, raw_jd_text=jd_text, db=db_session, use_live_llm=False)
    bob_dossier = crew_service.run_analysis(raw_resume_text=bob_text, raw_jd_text=jd_text, db=db_session, use_live_llm=False)
    charlie_dossier = crew_service.run_analysis(raw_resume_text=charlie_text, raw_jd_text=jd_text, db=db_session, use_live_llm=False)

    # Monotonic ranking check
    assert alice_dossier.overall_match_score > bob_dossier.overall_match_score
    assert bob_dossier.overall_match_score > charlie_dossier.overall_match_score

    # Score bounded strictly [0.0 - 100.0]
    for d in [alice_dossier, bob_dossier, charlie_dossier]:
        assert 0.0 <= d.overall_match_score <= 100.0
        assert 0.0 <= d.evidence_confidence_score <= 100.0
        assert len(d.key_strengths) > 0
        assert d.classification in ["STRONG_FIT", "POTENTIAL_FIT", "WEAK_FIT", "NOT_RECOMMENDED"]


def test_dossier_preserves_evidence_grounding_without_hallucination(db_session):
    """
    Verify candidate with zero registered local code repos has 0.0 evidence confidence,
    ensuring the agent does not fabricate evidence out of thin air.
    """
    resume_text = "Experienced with Python, Django, PostgreSQL, Kubernetes, Terraform, AWS, Docker."
    jd_text = "Senior Python engineer with Kubernetes and PostgreSQL."

    # Running with no project_ids and empty projects DB
    dossier = crew_service.run_analysis(
        raw_resume_text=resume_text,
        raw_jd_text=jd_text,
        project_ids=[],
        db=db_session,
        use_live_llm=False,
    )

    # Evidence confidence MUST be 0.0 when no projects are registered
    assert dossier.evidence_confidence_score == 0.0
    assert len(dossier.verified_skills) == 0
    # Every claimed skill should be UNVERIFIED in the absence of repositories
    assert len(dossier.unverified_skills) > 0
