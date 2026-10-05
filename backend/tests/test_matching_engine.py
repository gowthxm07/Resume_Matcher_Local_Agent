"""
Unit tests for deterministic matching engine scoring, boundaries, and reproducibility.
"""

import pytest
from app.services.matching_engine import MatchingEngine
from app.schemas.intelligence import (
    ResumeProfile,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem,
    JobProfile,
    MatchClassification,
    RequirementType,
)
from app.services.requirement_classifier import RequirementClassifier


@pytest.mark.asyncio
async def test_score_boundaries():
    """Verify composite and dimension scores are strictly bounded between 0 and 100."""
    engine = MatchingEngine()
    empty_resume = ResumeProfile()
    demanding_job = JobProfile(
        title="Staff AI Architect",
        required_skills=["C++", "CUDA", "PyTorch", "Kubernetes", "Distributed Systems"],
        preferred_skills=["Rust", "Triton"],
        categorized_requirements=RequirementClassifier.classify_requirements_list(
            required_skills=["C++", "CUDA", "PyTorch", "Kubernetes", "Distributed Systems"],
            preferred_skills=["Rust", "Triton"],
        ),
    )
    result = await engine.analyze_match(empty_resume, demanding_job)
    assert 0.0 <= result.overall_score <= 100.0
    assert 0.0 <= result.dimension_scores.required_skill_score <= 100.0
    assert 0.0 <= result.dimension_scores.preferred_skill_score <= 100.0


@pytest.mark.asyncio
async def test_reproducibility():
    """Verify repeated runs with identical inputs produce bit-exact identical scores."""
    engine = MatchingEngine()
    resume = ResumeProfile(
        skills=SkillsInventory(
            programming_languages=["Python", "SQL"],
            frameworks=["FastAPI"],
            databases=["PostgreSQL"],
        ),
        projects=[
            ProjectItem(
                name="API Service",
                description="FastAPI service with PostgreSQL",
                technologies=["Python", "FastAPI", "PostgreSQL"],
            )
        ],
    )
    job = JobProfile(
        title="Backend Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Docker"],
        categorized_requirements=RequirementClassifier.classify_requirements_list(
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            preferred_skills=["Docker"],
        ),
    )
    res1 = await engine.analyze_match(resume, job)
    res2 = await engine.analyze_match(resume, job)
    assert res1.overall_score == res2.overall_score
    assert res1.dimension_scores.required_skill_score == res2.dimension_scores.required_skill_score
    assert len(res1.matched_requirements) == len(res2.matched_requirements)


@pytest.mark.asyncio
async def test_match_classification_types():
    """Verify classifications: MATCH, PARTIAL_MATCH, MISSING."""
    engine = MatchingEngine()
    resume = ResumeProfile(
        skills=SkillsInventory(
            programming_languages=["Python"],
            databases=["MySQL"],  # Has MySQL, not PostgreSQL -> Partial match
        )
    )
    job = JobProfile(
        title="Data Engineer",
        required_skills=["Python", "PostgreSQL", "Rust"],
        categorized_requirements=RequirementClassifier.classify_requirements_list(
            required_skills=["Python", "PostgreSQL", "Rust"],
            preferred_skills=[],
        ),
    )
    result = await engine.analyze_match(resume, job)

    class_map = {r.canonical_skill: r.classification for r in result.requirements_analysis}
    assert class_map["Python"] == MatchClassification.MATCH
    assert class_map["PostgreSQL"] == MatchClassification.PARTIAL_MATCH
    assert class_map["Rust"] == MatchClassification.MISSING
