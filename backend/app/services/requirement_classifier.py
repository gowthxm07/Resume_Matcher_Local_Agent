"""
Requirement categorization and classification system for Job Descriptions.
Classifies extracted JD requirements into structured categories, importance weights,
and strict required vs preferred status.
"""

import re
from typing import List, Dict, Any, Optional
from app.schemas.intelligence import (
    CategorizedRequirement,
    RequirementType,
    SkillCategory,
)
from app.services.skill_normalizer import skill_normalizer


class RequirementClassifier:
    """
    Classifies raw requirements from job descriptions into structured categories,
    computes requirement importance, and enforces canonical normalization.
    """

    CRITICAL_KEYWORDS = ["must have", "required", "essential", "mandatory", "minimum", "need to have"]
    PREFERRED_KEYWORDS = ["nice to have", "plus", "preferred", "bonus", "optional", "desired", "advantageous"]

    @classmethod
    def classify_requirement(
        cls,
        req_text: str,
        is_explicitly_preferred: bool = False,
        min_years: Optional[float] = None,
    ) -> CategorizedRequirement:
        """
        Transform a raw JD requirement string into a CategorizedRequirement.
        """
        cleaned = req_text.strip()
        lowered = cleaned.lower()

        # 1. Determine requirement type
        req_type = RequirementType.PREFERRED if is_explicitly_preferred else RequirementType.REQUIRED
        if any(kw in lowered for kw in RequirementClassifier.PREFERRED_KEYWORDS):
            req_type = RequirementType.PREFERRED
        elif any(kw in lowered for kw in RequirementClassifier.CRITICAL_KEYWORDS):
            req_type = RequirementType.REQUIRED

        # 2. Extract canonical skill if identifiable
        canonical = skill_normalizer.normalize(cleaned)
        category = skill_normalizer.get_category(canonical)

        # If direct normalization didn't identify a catalog skill, scan for known skills in text
        if category == SkillCategory.OTHER:
            found_skills = skill_normalizer.find_all_known_skills(cleaned)
            if found_skills:
                canonical = found_skills[0]
                category = skill_normalizer.get_category(canonical)

        # 3. If category is still OTHER, apply heuristic pattern categorization
        if category == SkillCategory.OTHER:
            if any(term in lowered for term in ["architecture", "system design", "distributed systems", "microservices"]):
                category = SkillCategory.ARCHITECTURE
            elif re.search(r"\b(?:degree|bachelor|master|phd|bs|ms|b\.s\.|m\.s\.|computer science)\b", lowered):
                category = SkillCategory.EDUCATION
            elif any(term in lowered for term in ["test", "qa", "quality assurance", "pytest", "unit test"]):
                category = SkillCategory.TESTING
            elif any(term in lowered for term in ["communication", "leadership", "teamwork", "collaborat", "problem-solving"]):
                category = SkillCategory.SOFT_SKILL
            elif any(term in lowered for term in ["agile", "scrum", "jira"]):
                category = SkillCategory.TOOL
            elif any(term in lowered for term in ["year", "years", "experience", "senior", "lead", "proven track record"]):
                category = SkillCategory.EXPERIENCE

        # 4. Extract years of experience if mentioned in text
        extracted_years = min_years
        if extracted_years is None:
            year_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*years?", lowered)
            if year_match:
                try:
                    extracted_years = float(year_match.group(1))
                except ValueError:
                    pass

        # 5. Compute importance
        importance = "medium"
        if req_type == RequirementType.REQUIRED:
            if category in [SkillCategory.PROGRAMMING_LANGUAGE, SkillCategory.FRAMEWORK, SkillCategory.DATABASE]:
                importance = "critical"
            else:
                importance = "high"
        else:
            importance = "low" if category == SkillCategory.SOFT_SKILL else "medium"

        return CategorizedRequirement(
            canonical_skill=canonical,
            original_text=cleaned,
            requirement_type=req_type,
            category=category,
            importance=importance,
            min_years=extracted_years,
            confidence=0.95 if canonical in skill_normalizer._canonical_to_category else 0.80,
        )

    @classmethod
    def classify_requirements_list(
        cls,
        required_skills: List[str],
        preferred_skills: List[str],
    ) -> List[CategorizedRequirement]:
        """Classify both required and preferred requirement lists."""
        results: List[CategorizedRequirement] = []
        seen_canonicals = set()

        for req in required_skills:
            cr = cls.classify_requirement(req, is_explicitly_preferred=False)
            if cr.canonical_skill.lower() not in seen_canonicals:
                results.append(cr)
                seen_canonicals.add(cr.canonical_skill.lower())

        for req in preferred_skills:
            cr = cls.classify_requirement(req, is_explicitly_preferred=True)
            if cr.canonical_skill.lower() not in seen_canonicals:
                results.append(cr)
                seen_canonicals.add(cr.canonical_skill.lower())

        return results
