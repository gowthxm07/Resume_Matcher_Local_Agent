"""
Explainable, deterministic matching engine for CareerCrew.
Evaluates candidate ResumeProfile against JobProfile across 7 distinct dimensions.
Produces reproducible composite scores strictly bounded between 0 and 100 with grounded evidence.
"""

import time
from typing import Dict, Any, List, Optional, Tuple, Set
from app.core.logging import logger
from app.schemas.intelligence import (
    ResumeProfile,
    JobProfile,
    CategorizedRequirement,
    RequirementType,
    SkillCategory,
    MatchClassification,
    RequirementMatchResult,
    DimensionScores,
    AnalysisResult,
    AnalysisMetadata,
    ProjectRelevanceItem,
)
from app.services.skill_normalizer import skill_normalizer
from app.services.project_relevance import project_relevance_service


DEFAULT_WEIGHTS = {
    "required_skill_coverage": 0.35,
    "preferred_skill_coverage": 0.15,
    "technical_depth": 0.15,
    "project_relevance": 0.15,
    "experience_alignment": 0.10,
    "education_alignment": 0.05,
    "keyword_coverage": 0.05,
}


class MatchingEngine:
    """
    Computes explainable, reproducible match analysis between a candidate ResumeProfile
    and a target JobProfile.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS
        # Normalize weights so they sum to 1.0
        total_w = sum(self.weights.values())
        if total_w > 0:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

    async def analyze_match(
        self,
        resume: ResumeProfile,
        job: JobProfile,
        resume_id: Optional[str] = None,
        job_description_id: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Execute full deterministic and semantic baseline match assessment.
        """
        start_time = time.perf_counter()

        # 1. Build candidate's normalized skills set and evidence map
        candidate_skills_set, skill_evidence_map = self._build_candidate_evidence_map(resume)

        # 2. Evaluate all categorized requirements
        requirements_results: List[RequirementMatchResult] = []
        matched_reqs: List[RequirementMatchResult] = []
        partial_reqs: List[RequirementMatchResult] = []
        missing_reqs: List[RequirementMatchResult] = []

        req_skills_total = 0
        req_skills_score_sum = 0.0
        pref_skills_total = 0
        pref_skills_score_sum = 0.0

        for req in job.categorized_requirements:
            res = self._evaluate_single_requirement(req, candidate_skills_set, skill_evidence_map, resume)
            requirements_results.append(res)

            if res.classification == MatchClassification.MATCH:
                matched_reqs.append(res)
                score_contrib = 1.0
            elif res.classification == MatchClassification.PARTIAL_MATCH:
                partial_reqs.append(res)
                score_contrib = 0.5
            else:
                missing_reqs.append(res)
                score_contrib = 0.0

            if req.requirement_type == RequirementType.REQUIRED:
                req_skills_total += 1
                req_skills_score_sum += score_contrib
            else:
                pref_skills_total += 1
                pref_skills_score_sum += score_contrib

        # Calculate coverage scores (0 - 100)
        required_score = (
            (req_skills_score_sum / req_skills_total * 100.0)
            if req_skills_total > 0
            else 100.0
        )
        preferred_score = (
            (pref_skills_score_sum / pref_skills_total * 100.0)
            if pref_skills_total > 0
            else 100.0
        )

        # 3. Technical Depth Score
        # Rewards using matching technologies across multiple projects/work experiences
        tech_depth_score = self._compute_technical_depth(matched_reqs, skill_evidence_map)

        # 4. Semantic Project Relevance
        project_rel_score, project_items = await project_relevance_service.evaluate_projects(resume, job)

        # 5. Experience Alignment Score
        exp_score = self._compute_experience_alignment(resume, job)

        # 6. Education Alignment Score
        edu_score = self._compute_education_alignment(resume, job)

        # 7. Keyword Coverage Score
        kw_score = self._compute_keyword_coverage(resume, job)

        # Compute Weighted Overall Score
        overall = (
            (required_score * self.weights["required_skill_coverage"])
            + (preferred_score * self.weights["preferred_skill_coverage"])
            + (tech_depth_score * self.weights["technical_depth"])
            + (project_rel_score * self.weights["project_relevance"])
            + (exp_score * self.weights["experience_alignment"])
            + (edu_score * self.weights["education_alignment"])
            + (kw_score * self.weights["keyword_coverage"])
        )
        bounded_overall = round(max(0.0, min(100.0, overall)), 1)

        dim_scores = DimensionScores(
            required_skill_score=round(required_score, 1),
            preferred_skill_score=round(preferred_score, 1),
            technical_depth_score=round(tech_depth_score, 1),
            project_relevance_score=round(project_rel_score, 1),
            experience_alignment_score=round(exp_score, 1),
            education_alignment_score=round(edu_score, 1),
            keyword_coverage_score=round(kw_score, 1),
        )

        # Generate strong areas, weak areas, and summary explanation
        strong_areas = [m.canonical_skill for m in matched_reqs[:6]]
        weak_areas = [m.canonical_skill for m in missing_reqs if m.requirement_type == RequirementType.REQUIRED][:6]

        summary = self._generate_summary_explanation(
            bounded_overall,
            dim_scores,
            matched_reqs,
            missing_reqs,
            job,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return AnalysisResult(
            overall_score=bounded_overall,
            dimension_scores=dim_scores,
            scoring_weights={k: round(v, 3) for k, v in self.weights.items()},
            requirements_analysis=requirements_results,
            matched_requirements=matched_reqs,
            partial_matches=partial_reqs,
            missing_requirements=missing_reqs,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            project_relevance=project_items,
            summary_explanation=summary,
            resume_id=resume_id,
            job_description_id=job_description_id,
            metadata=AnalysisMetadata(
                analysis_time_ms=round(elapsed_ms, 2),
            ),
        )

    def _build_candidate_evidence_map(
        self, resume: ResumeProfile
    ) -> Tuple[Set[str], Dict[str, List[str]]]:
        """
        Scan resume skills, experience, and projects to index every skill and its sources.
        """
        skills_set: Set[str] = set()
        evidence_map: Dict[str, List[str]] = {}

        # 1. Skills inventory
        for s in resume.skills.all_technical_skills():
            canon = skill_normalizer.normalize(s)
            skills_set.add(canon.lower())
            evidence_map.setdefault(canon.lower(), []).append("Listed in Core Skills")

        # 2. Work experiences
        for w in resume.work_experience:
            source_tag = f"Experience at {w.organization} ({w.role})"
            for t in w.technologies:
                canon = skill_normalizer.normalize(t)
                skills_set.add(canon.lower())
                evidence_map.setdefault(canon.lower(), []).append(source_tag)

            # Check text of responsibilities for skills
            full_exp_text = " ".join(w.responsibilities + w.measurable_achievements)
            found = skill_normalizer.find_all_known_skills(full_exp_text)
            for f in found:
                skills_set.add(f.lower())
                evidence_map.setdefault(f.lower(), []).append(source_tag)

        # 3. Projects
        for p in resume.projects:
            source_tag = f"Project '{p.name}'"
            for t in p.technologies:
                canon = skill_normalizer.normalize(t)
                skills_set.add(canon.lower())
                evidence_map.setdefault(canon.lower(), []).append(source_tag)

            full_proj_text = f"{p.description} {' '.join(p.responsibilities)} {' '.join(p.measurable_results)}"
            found = skill_normalizer.find_all_known_skills(full_proj_text)
            for f in found:
                skills_set.add(f.lower())
                evidence_map.setdefault(f.lower(), []).append(source_tag)

        return skills_set, evidence_map

    def _evaluate_single_requirement(
        self,
        req: CategorizedRequirement,
        candidate_skills: Set[str],
        evidence_map: Dict[str, List[str]],
        resume: ResumeProfile,
    ) -> RequirementMatchResult:
        """
        Classify candidate match for a specific requirement.
        """
        canon_lowered = req.canonical_skill.lower()

        # Check Exact Match
        if canon_lowered in candidate_skills:
            evidence = evidence_map.get(canon_lowered, ["Identified in resume"])
            # Deduplicate evidence
            deduped_ev = list(dict.fromkeys(evidence))
            expl = f"{req.canonical_skill} is verified in candidate profile ({', '.join(deduped_ev[:2])})."
            return RequirementMatchResult(
                requirement=req.original_text,
                canonical_skill=req.canonical_skill,
                requirement_type=req.requirement_type,
                category=req.category,
                classification=MatchClassification.MATCH,
                candidate_evidence=deduped_ev,
                confidence=1.0,
                explanation=expl,
            )

        # Check Partial Match (related skill or category overlap)
        partial_match_found = False
        partial_evidence: List[str] = []
        partial_reason = ""

        # Category-based partial overlap heuristics
        if req.category == SkillCategory.DATABASE:
            # If candidate knows another major DB
            candidate_dbs = [s for s in resume.skills.databases if skill_normalizer.get_category(s) == SkillCategory.DATABASE]
            if candidate_dbs:
                partial_match_found = True
                partial_evidence.extend(candidate_dbs[:2])
                partial_reason = f"Candidate has database experience with {', '.join(candidate_dbs[:2])}, providing partial transferability for {req.canonical_skill}."

        elif req.category == SkillCategory.CLOUD:
            candidate_clouds = [s for s in resume.skills.cloud_platforms if s]
            if candidate_clouds:
                partial_match_found = True
                partial_evidence.extend(candidate_clouds[:2])
                partial_reason = f"Candidate has cloud infrastructure experience with {', '.join(candidate_clouds[:2])}."

        elif req.category == SkillCategory.FRAMEWORK:
            # Related framework e.g. Flask when FastAPI is requested
            if req.canonical_skill.lower() == "fastapi" and any("flask" in s.lower() or "django" in s.lower() for s in candidate_skills):
                partial_match_found = True
                partial_evidence.append("Python Web Frameworks")
                partial_reason = f"Candidate has Python web framework experience related to {req.canonical_skill}."

        if partial_match_found:
            return RequirementMatchResult(
                requirement=req.original_text,
                canonical_skill=req.canonical_skill,
                requirement_type=req.requirement_type,
                category=req.category,
                classification=MatchClassification.PARTIAL_MATCH,
                candidate_evidence=partial_evidence,
                confidence=0.75,
                explanation=partial_reason,
            )

        # Missing
        req_label = "Required" if req.requirement_type == RequirementType.REQUIRED else "Preferred"
        return RequirementMatchResult(
            requirement=req.original_text,
            canonical_skill=req.canonical_skill,
            requirement_type=req.requirement_type,
            category=req.category,
            classification=MatchClassification.MISSING,
            candidate_evidence=[],
            confidence=0.95,
            explanation=f"{req_label} skill '{req.canonical_skill}' was not found in candidate skills, experiences, or project repositories.",
        )

    def _compute_technical_depth(
        self,
        matched_reqs: List[RequirementMatchResult],
        evidence_map: Dict[str, List[str]],
    ) -> float:
        """
        Measures depth: candidates who have applied a skill in multiple places (skills + work + projects)
        receive higher depth scores than those who only list it once.
        """
        if not matched_reqs:
            return 0.0

        depth_sum = 0.0
        for m in matched_reqs:
            evidences = evidence_map.get(m.canonical_skill.lower(), [])
            # 1 evidence source = 60%, 2 sources = 85%, 3+ sources = 100%
            if len(evidences) >= 3:
                depth_sum += 1.0
            elif len(evidences) == 2:
                depth_sum += 0.85
            else:
                depth_sum += 0.60

        return max(0.0, min(100.0, (depth_sum / len(matched_reqs)) * 100.0))

    def _compute_experience_alignment(
        self, resume: ResumeProfile, job: JobProfile
    ) -> float:
        """Estimate candidate experience alignment against JD requirements."""
        if job.min_years_experience is None or job.min_years_experience <= 0:
            return 85.0  # Neutral high score if no strict years required

        # Estimate candidate years of experience based on work experience blocks
        # Default ~1.5 years per distinct work role if dates not parsed
        exp_count = len(resume.work_experience) + (len(resume.internships) * 0.5)
        estimated_years = max(1.0, exp_count * 1.5)

        ratio = estimated_years / job.min_years_experience
        if ratio >= 1.0:
            return 100.0
        elif ratio >= 0.7:
            return 80.0
        elif ratio >= 0.5:
            return 60.0
        else:
            return 40.0

    def _compute_education_alignment(
        self, resume: ResumeProfile, job: JobProfile
    ) -> float:
        """Evaluate academic degree alignment."""
        if not job.education_requirements:
            return 90.0

        if not resume.education:
            return 50.0

        # Check for degree keywords
        all_candidate_edu = " ".join([f"{e.degree} {e.field_of_study or ''}" for e in resume.education]).lower()
        all_jd_edu = " ".join(job.education_requirements).lower()

        if "master" in all_jd_edu or "phd" in all_jd_edu:
            if "master" in all_candidate_edu or "phd" in all_candidate_edu or "m.s." in all_candidate_edu:
                return 100.0
            return 75.0  # Candidate has bachelor's

        if "bachelor" in all_jd_edu or "b.s." in all_jd_edu or "degree" in all_jd_edu:
            if any(term in all_candidate_edu for term in ["bachelor", "b.s.", "bs", "master", "m.s.", "phd"]):
                return 100.0
            return 60.0

        return 85.0

    def _compute_keyword_coverage(
        self, resume: ResumeProfile, job: JobProfile
    ) -> float:
        """Evaluate broader contextual term coverage."""
        candidate_tokens = set(skill_normalizer.find_all_known_skills(
            " ".join(
                [resume.summary or ""]
                + [p.description for p in resume.projects]
                + [r for w in resume.work_experience for r in w.responsibilities]
            )
        ))

        target_tokens = set(skill_normalizer.find_all_known_skills(
            " ".join(job.responsibilities + job.domain_knowledge)
        ))

        if not target_tokens:
            return 80.0

        overlap = len(candidate_tokens.intersection(target_tokens))
        return max(0.0, min(100.0, (overlap / len(target_tokens)) * 100.0))

    def _generate_summary_explanation(
        self,
        overall_score: float,
        dim_scores: DimensionScores,
        matched: List[RequirementMatchResult],
        missing: List[RequirementMatchResult],
        job: JobProfile,
    ) -> str:
        """Generate human-readable summary of the match assessment."""
        req_missing = [m.canonical_skill for m in missing if m.requirement_type == RequirementType.REQUIRED]

        if overall_score >= 80.0:
            fit_tier = "Strong Candidate Fit"
        elif overall_score >= 60.0:
            fit_tier = "Moderate Alignment"
        else:
            fit_tier = "Low Direct Fit"

        summary = (
            f"{fit_tier} ({overall_score:.1f}%). Candidate satisfies {len(matched)} identified competencies "
            f"for '{job.title}'. Required skill coverage is {dim_scores.required_skill_score:.1f}%, with "
            f"project relevance scored at {dim_scores.project_relevance_score:.1f}%."
        )

        if req_missing:
            summary += f" Key critical gaps to address: {', '.join(req_missing[:3])}."
        else:
            summary += " All critical required skills are present in the candidate profile."

        return summary


# Global matching engine singleton
matching_engine = MatchingEngine()
