"""
Unit tests for semantic and lexical project relevance calculations.
"""

import pytest
from app.services.project_relevance import (
    cosine_similarity,
    lexical_jaccard_similarity,
    ProjectRelevanceService,
)
from app.schemas.intelligence import ResumeProfile, JobProfile, ProjectItem


def test_cosine_similarity_edge_cases():
    """Verify cosine similarity mathematical boundary behavior."""
    # Identical vectors -> 1.0
    v1 = [1.0, 2.0, 3.0]
    assert pytest.approx(cosine_similarity(v1, v1), 0.001) == 1.0

    # Orthogonal vectors -> 0.0
    v2 = [1.0, 0.0]
    v3 = [0.0, 1.0]
    assert cosine_similarity(v2, v3) == 0.0

    # Zero vector -> 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_lexical_jaccard_similarity():
    """Verify lexical token overlap calculation."""
    s1 = "Python FastAPI PostgreSQL"
    s2 = "FastAPI PostgreSQL backend"
    sim = lexical_jaccard_similarity(s1, s2)
    assert 0.0 < sim < 1.0
    assert lexical_jaccard_similarity(s1, s1) == 1.0
    assert lexical_jaccard_similarity("React", "Rust") == 0.0


@pytest.mark.asyncio
async def test_evaluate_projects_no_projects():
    """Verify empty project list returns baseline neutral score."""
    resume = ResumeProfile(projects=[])
    job = JobProfile(required_skills=["Python"])
    score, items = await ProjectRelevanceService.evaluate_projects(resume, job)
    assert score == 30.0
    assert len(items) == 0


@pytest.mark.asyncio
async def test_evaluate_projects_with_matching_tech():
    """Verify projects utilizing JD skills achieve high relevance scores."""
    resume = ResumeProfile(
        projects=[
            ProjectItem(
                name="E-Commerce API",
                description="Built high-performance payment microservice with Python, FastAPI, and PostgreSQL.",
                technologies=["Python", "FastAPI", "PostgreSQL"],
            )
        ]
    )
    job = JobProfile(
        title="Python Backend Developer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
    )
    score, items = await ProjectRelevanceService.evaluate_projects(resume, job)
    assert score >= 50.0
    assert len(items) == 1
    assert items[0].project_name == "E-Commerce API"
    assert "FastAPI" in items[0].matched_themes
