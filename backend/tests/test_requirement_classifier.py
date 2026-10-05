"""
Unit tests for Job Description requirement classification and categorization.
"""

from app.services.requirement_classifier import RequirementClassifier
from app.schemas.intelligence import RequirementType, SkillCategory


def test_classify_required_skill():
    """Verify mandatory requirements receive REQUIRED status and critical importance."""
    req = RequirementClassifier.classify_requirement("Must have 5+ years of Python")
    assert req.canonical_skill == "Python"
    assert req.requirement_type == RequirementType.REQUIRED
    assert req.category == SkillCategory.PROGRAMMING_LANGUAGE
    assert req.importance in ["critical", "high"]
    assert req.min_years == 5.0


def test_classify_preferred_skill():
    """Verify nice-to-have requirements receive PREFERRED status."""
    req = RequirementClassifier.classify_requirement("Knowledge of Docker is a plus")
    assert req.canonical_skill == "Docker"
    assert req.requirement_type == RequirementType.PREFERRED
    assert req.category == SkillCategory.DEVOPS


def test_classify_education_requirement():
    """Verify degree requirements are categorized as EDUCATION."""
    req = RequirementClassifier.classify_requirement("Bachelor's degree in Computer Science")
    assert req.category == SkillCategory.EDUCATION


def test_classify_architecture_requirement():
    """Verify architecture requirements are categorized as ARCHITECTURE."""
    req = RequirementClassifier.classify_requirement("Experience in Microservices and Distributed Systems")
    assert req.category == SkillCategory.ARCHITECTURE
