"""
Deterministic Applicant Tracking System (ATS) validation and heuristic scoring engine.
Evaluates parseability, section structure, keyword coverage, keyword stuffing, and formatting risks.
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from app.schemas.optimization import ATSValidationResult
from app.services.skill_normalizer import SkillNormalizer, skill_normalizer


STANDARD_SECTIONS = [
    "Summary",
    "Experience",
    "Projects",
    "Skills",
    "Education",
    "Certifications",
    "Achievements",
]

SECTION_PATTERNS = {
    "Summary": [r"\b(?:professional\s+)?summary\b", r"\bobjective\b", r"\bprofile\b", r"\babout\s+me\b"],
    "Experience": [r"\b(?:work|professional)?\s*experience\b", r"\bemployment\s+history\b", r"\bwork\s+history\b"],
    "Projects": [r"\b(?:key\s+)?projects\b", r"\bpersonal\s+projects\b", r"\btechnical\s+projects\b"],
    "Skills": [r"\b(?:technical\s+)?skills\b", r"\bcore\s+competencies\b", r"\btechnologies\b", r"\btech\s+stack\b"],
    "Education": [r"\beducation\b", r"\bacademics\b", r"\bacacademic\s+background\b"],
    "Certifications": [r"\bcertifications?\b", r"\blicenses?\b", r"\bcredentials\b"],
    "Achievements": [r"\bachievements?\b", r"\bawards?\b", r"\bhono(?:u)?rs\b"],
}

DISCLAIMER_TEXT = (
    "ATS scores are heuristic estimates of machine parseability and keyword alignment, "
    "not guarantees of employer ATS platform outcomes."
)


class ATSService:
    """
    Deterministic ATS validator providing multi-dimensional compatibility auditing
    and heuristic ATS scoring.
    """

    @classmethod
    def validate_ats_compatibility(
        cls,
        resume_text: str,
        job_profile: Any,
    ) -> ATSValidationResult:
        """Convenience method accepting structured JobProfile object."""
        req = getattr(job_profile, "required_skills", [])
        pref = getattr(job_profile, "preferred_skills", [])
        return cls.evaluate_resume(resume_text, required_skills=req, preferred_skills=pref)

    @classmethod
    def evaluate_resume(
        cls,
        resume_text: str,
        required_skills: Optional[List[str]] = None,
        preferred_skills: Optional[List[str]] = None,
        job_description_text: Optional[str] = None,
    ) -> ATSValidationResult:
        """
        Perform complete deterministic ATS compatibility analysis on resume text
        in relation to target job requirements.
        """
        required_skills = required_skills or []
        preferred_skills = preferred_skills or []

        # If job text is provided but skills are empty, extract rudimentary skills using normalizer
        if not required_skills and job_description_text:
            extracted = skill_normalizer.find_all_known_skills(job_description_text)
            required_skills = extracted[:8]
            preferred_skills = extracted[8:15]

        # 1. Parseability evaluation
        parseability_score, parse_hazards = cls._audit_parseability(resume_text)

        # 2. Section structure audit
        structure_score, identified_sections, missing_sections = cls._audit_sections(resume_text)

        # 3. Required skills coverage
        req_score, matched_req, missing_req = cls._audit_skill_coverage(resume_text, required_skills)

        # 4. Preferred skills coverage
        pref_score, matched_pref, missing_pref = cls._audit_skill_coverage(resume_text, preferred_skills)

        # 5. Keyword distribution & stuffing detection
        all_target_skills = list(set(required_skills + preferred_skills))
        stuffing_keywords, distribution_score = cls._audit_keyword_distribution(resume_text, all_target_skills)

        # 6. Formatting hazards
        formatting_hazards = list(parse_hazards)
        formatting_safety_score, extra_hazards = cls._audit_formatting(resume_text)
        formatting_hazards.extend(extra_hazards)

        # 7. Composite heuristic score
        # Base weights: Parseability 20%, Structure 15%, Req Skills 35%, Pref Skills 15%, Distribution & Safety 15%
        dist_and_safety = (distribution_score * 0.5) + (formatting_safety_score * 0.5)
        raw_score = (
            (parseability_score * 0.20)
            + (structure_score * 0.15)
            + (req_score * 0.35)
            + (pref_score * 0.15)
            + (dist_and_safety * 0.15)
        )

        # Keyword stuffing penalty: -15 pts per stuffed keyword up to -30
        stuffing_penalty = min(len(stuffing_keywords) * 15.0, 30.0)
        overall_ats_score = max(0.0, min(100.0, round(raw_score - stuffing_penalty, 1)))

        is_compliant = overall_ats_score >= 60.0 and len(stuffing_keywords) == 0 and len(formatting_hazards) <= 2

        return ATSValidationResult(
            overall_ats_score=overall_ats_score,
            parseability_score=round(parseability_score, 1),
            section_structure_score=round(structure_score, 1),
            required_skill_coverage_score=round(req_score, 1),
            preferred_skill_coverage_score=round(pref_score, 1),
            keyword_distribution_score=round(distribution_score, 1),
            formatting_safety_score=round(formatting_safety_score, 1),
            identified_sections=identified_sections,
            missing_standard_sections=missing_sections,
            matched_required_skills=matched_req,
            missing_required_skills=missing_req,
            matched_preferred_skills=matched_pref,
            missing_preferred_skills=missing_pref,
            detected_stuffing_keywords=stuffing_keywords,
            formatting_hazards=list(set(formatting_hazards)),
            is_ats_compliant=is_compliant,
            disclaimer=DISCLAIMER_TEXT,
        )

    @classmethod
    def _audit_parseability(cls, text: str) -> Tuple[float, List[str]]:
        """Audit whether resume text is clean, extractable, and free of corruption."""
        hazards = []
        if not text or not text.strip():
            return 0.0, ["Empty resume text provided"]

        cleaned = text.strip()
        length = len(cleaned)

        if length < 100:
            hazards.append("Resume text is critically short (< 100 characters)")
            return 30.0, hazards

        # Check for unprintable/control characters (excluding common whitespace)
        control_chars = [c for c in cleaned if ord(c) < 32 and c not in ("\n", "\r", "\t")]
        control_ratio = len(control_chars) / max(length, 1)

        score = 100.0
        if control_ratio > 0.01:
            hazards.append(f"Excessive control characters detected ({len(control_chars)} control bytes)")
            score -= 40.0
        elif control_ratio > 0.002:
            hazards.append("Minor control characters detected")
            score -= 15.0

        # Check line structure
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if len(lines) < 5:
            hazards.append("Unusually low line count for resume structure")
            score -= 20.0

        return max(0.0, min(100.0, score)), hazards

    @classmethod
    def _audit_sections(cls, text: str) -> Tuple[float, List[str], List[str]]:
        """Identify recognized standard section headers."""
        identified: List[str] = []
        missing: List[str] = []

        lower_text = text.lower()
        lines = [line.strip().lower() for line in text.splitlines() if line.strip()]

        for section, patterns in SECTION_PATTERNS.items():
            found = False
            for pat in patterns:
                # Header match check: on its own line or with colon/divider
                for line in lines:
                    if len(line) < 40 and re.search(pat, line):
                        found = True
                        break
                if not found and re.search(r"(?:^|\n)\s*" + pat + r"\s*[:\n]", lower_text):
                    found = True
                if found:
                    break

            if found:
                identified.append(section)
            else:
                missing.append(section)

        # Scoring: having 4+ standard sections scores 100%, 3 scores 80%, 2 scores 60%, 1 scores 35%
        count = len(identified)
        if count >= 4:
            score = 100.0
        elif count == 3:
            score = 80.0
        elif count == 2:
            score = 60.0
        elif count == 1:
            score = 35.0
        else:
            score = 10.0

        return score, identified, missing

    @classmethod
    def _audit_skill_coverage(
        cls, text: str, skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate coverage percentage of specified skills in text."""
        if not skills:
            return 100.0, [], []

        lower_text = text.lower()
        matched: List[str] = []
        missing: List[str] = []

        for skill in skills:
            norm_skill = skill_normalizer.normalize(skill)
            # Match either exact skill, normalized skill, or word boundary
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            norm_pattern = r"\b" + re.escape(norm_skill.lower()) + r"\b"

            if re.search(pattern, lower_text) or re.search(norm_pattern, lower_text) or skill.lower() in lower_text:
                matched.append(skill)
            else:
                missing.append(skill)

        score = (len(matched) / len(skills)) * 100.0 if skills else 100.0
        return round(score, 1), matched, missing

    @classmethod
    def _audit_keyword_distribution(
        cls, text: str, target_skills: List[str]
    ) -> Tuple[List[str], float]:
        """Detect keyword stuffing and analyze keyword distribution balance."""
        if not text or not target_skills:
            return [], 100.0

        lower_text = text.lower()
        words = re.findall(r"\b[a-zA-Z0-9_\-\.\#\+]+\b", lower_text)
        total_word_count = max(len(words), 1)

        stuffing_keywords: List[str] = []
        # Check occurrences of each target skill
        for skill in target_skills:
            skill_clean = skill.strip().lower()
            if not skill_clean or len(skill_clean) < 2:
                continue
            # Count occurrences
            pattern = r"\b" + re.escape(skill_clean) + r"\b"
            matches = len(re.findall(pattern, lower_text))

            # Stuffing threshold: > 6 occurrences or > 3.5% of total words in a typical 400-word resume
            if matches >= 7 or (matches >= 5 and (matches / total_word_count) > 0.04):
                stuffing_keywords.append(skill)

        # Distribution score: deduct points if stuffing exists
        score = 100.0 - (len(stuffing_keywords) * 25.0)
        return stuffing_keywords, max(0.0, min(100.0, score))

    @classmethod
    def _audit_formatting(cls, text: str) -> Tuple[float, List[str]]:
        """Detect parser-hostile formatting patterns like massive unbroken lines or empty headers."""
        hazards: List[str] = []
        score = 100.0
        lines = text.splitlines()

        # Check for extremely long lines without punctuation (> 350 chars)
        long_lines = [l for l in lines if len(l.strip()) > 350 and "." not in l]
        if long_lines:
            hazards.append(f"Detected {len(long_lines)} extremely long unbroken lines (> 350 characters)")
            score -= 20.0

        # Check for repetitive consecutive blank lines (> 4 blank lines in a row)
        blank_streak = 0
        max_blank = 0
        for l in lines:
            if not l.strip():
                blank_streak += 1
                max_blank = max(max_blank, blank_streak)
            else:
                blank_streak = 0
        if max_blank >= 5:
            hazards.append(f"Excessive blank line spacing ({max_blank} consecutive blank lines)")
            score -= 10.0

        # Check for non-standard symbol spam
        symbol_spam = re.findall(r"[\*\|\~]{4,}", text)
        if symbol_spam:
            hazards.append("Detected decorative ASCII symbol repetition that impairs parser AST")
            score -= 15.0

        return max(0.0, min(100.0, score)), hazards


ats_service = ATSService()
