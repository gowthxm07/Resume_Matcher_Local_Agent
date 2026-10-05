"""
Unit tests for deterministic skill normalization and alias resolution.
Verifies canonical mappings and strict negative boundaries (e.g., Java != JavaScript).
"""

import pytest
from app.services.skill_normalizer import skill_normalizer
from app.schemas.intelligence import SkillCategory


def test_javascript_normalization():
    """Verify JavaScript aliases resolve to canonical 'JavaScript'."""
    aliases = ["javascript", "js", "JS", "ecmascript", "es6", "vanilla js"]
    for a in aliases:
        assert skill_normalizer.normalize(a) == "JavaScript", f"Failed for '{a}'"


def test_postgresql_normalization():
    """Verify PostgreSQL aliases resolve to canonical 'PostgreSQL'."""
    aliases = ["postgresql", "postgres", "psql", "pgsql", "postgresql db"]
    for a in aliases:
        assert skill_normalizer.normalize(a) == "PostgreSQL", f"Failed for '{a}'"


def test_nodejs_normalization():
    """Verify Node.js aliases resolve to canonical 'Node.js'."""
    aliases = ["nodejs", "node.js", "node", "node js"]
    for a in aliases:
        assert skill_normalizer.normalize(a) == "Node.js", f"Failed for '{a}'"


def test_docker_and_kubernetes_normalization():
    """Verify Docker and K8s normalization."""
    assert skill_normalizer.normalize("docker") == "Docker"
    assert skill_normalizer.normalize("docker container") == "Docker"
    assert skill_normalizer.normalize("k8s") == "Kubernetes"
    assert skill_normalizer.normalize("kubernetes") == "Kubernetes"


def test_negative_boundaries_no_false_equivalence():
    """
    CRITICAL: Verify negative boundaries prevent false equivalences:
    - Java != JavaScript
    - C != C++ != C#
    """
    assert not skill_normalizer.are_equivalent("Java", "JavaScript")
    assert not skill_normalizer.are_equivalent("java", "js")
    assert not skill_normalizer.are_equivalent("C", "C++")
    assert not skill_normalizer.are_equivalent("C++", "C#")
    assert not skill_normalizer.are_equivalent("Python", "PHP")
    assert not skill_normalizer.are_equivalent("TypeScript", "JavaScript")


def test_positive_equivalences():
    """Verify positive equivalences return True."""
    assert skill_normalizer.are_equivalent("JS", "JavaScript")
    assert skill_normalizer.are_equivalent("postgres", "PostgreSQL")
    assert skill_normalizer.are_equivalent("k8s", "Kubernetes")
    assert skill_normalizer.are_equivalent("node", "Node.js")
    assert skill_normalizer.are_equivalent("fastapi", "FastAPI")


def test_category_lookup():
    """Verify category lookups for canonical skills."""
    assert skill_normalizer.get_category("Python") == SkillCategory.PROGRAMMING_LANGUAGE
    assert skill_normalizer.get_category("FastAPI") == SkillCategory.FRAMEWORK
    assert skill_normalizer.get_category("PostgreSQL") == SkillCategory.DATABASE
    assert skill_normalizer.get_category("AWS") == SkillCategory.CLOUD
    assert skill_normalizer.get_category("Docker") == SkillCategory.DEVOPS
    assert skill_normalizer.get_category("Git") == SkillCategory.TOOL


def test_find_all_known_skills():
    """Verify scanner extracts multiple known skills from raw prose text."""
    prose = "Candidate developed scalable backend microservices using Python, FastAPI, and PostgreSQL with Docker in AWS."
    skills = skill_normalizer.find_all_known_skills(prose)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "AWS" in skills
    assert "Java" not in skills  # Must not falsely match Java inside JavaScript or Python
