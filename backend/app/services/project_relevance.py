"""
Semantic project relevance evaluation using local Ollama embeddings.
Computes cosine similarity between candidate project descriptions and target job requirements.
Zero cloud embedding APIs.
"""

import math
from typing import List, Dict, Any, Tuple
from app.core.logging import logger
from app.services.embedding_service import embedding_service
from app.schemas.intelligence import (
    ResumeProfile,
    JobProfile,
    ProjectRelevanceItem,
    ProjectItem,
)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a, b in zip(vec_a, vec_b)))
    norm_b = math.sqrt(sum(b * b for a, b in zip(vec_a, vec_b)))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def lexical_jaccard_similarity(text_a: str, text_b: str) -> float:
    """Fallback lexical similarity between two text strings."""
    tokens_a = set(re_tokenize(text_a))
    tokens_b = set(re_tokenize(text_b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / len(union)


def re_tokenize(text: str) -> List[str]:
    import re
    return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_\-\+\#]{2,}\b", text)]


class ProjectRelevanceService:
    """
    Evaluates semantic and technical alignment between candidate project descriptions
    and target job description responsibilities.
    """

    @classmethod
    async def evaluate_projects(
        cls,
        resume: ResumeProfile,
        job: JobProfile,
    ) -> Tuple[float, List[ProjectRelevanceItem]]:
        """
        Compute project relevance score (0.0 to 100.0) and detailed item breakdown.
        """
        projects: List[ProjectItem] = resume.projects
        if not projects:
            logger.info("Resume has no listed projects; assigning baseline neutral relevance")
            return 30.0, []

        # Combine key JD target text for comparison
        jd_targets = []
        if job.responsibilities:
            jd_targets.extend(job.responsibilities)
        if job.required_skills:
            jd_targets.append(f"Required skills: {', '.join(job.required_skills)}")
        if job.preferred_skills:
            jd_targets.append(f"Preferred skills: {', '.join(job.preferred_skills)}")
        if job.domain_knowledge:
            jd_targets.append(f"Domain: {', '.join(job.domain_knowledge)}")

        combined_jd_text = " ".join(jd_targets) if jd_targets else f"{job.title} at {job.company}"

        items: List[ProjectRelevanceItem] = []
        project_scores: List[float] = []

        # Try semantic embedding similarity first
        use_embeddings = False
        jd_embedding = None
        try:
            avail = await embedding_service.check_availability()
            if avail.get("available"):
                jd_embedding = await embedding_service.get_embedding(combined_jd_text[:1000])
                use_embeddings = True
        except Exception as exc:
            logger.debug(f"Local embedding model unavailable for project relevance: {exc}")
            use_embeddings = False

        for proj in projects:
            proj_text = f"{proj.name}. {proj.description}. Technologies: {', '.join(proj.technologies)}"
            sim_score = 0.0

            if use_embeddings and jd_embedding:
                try:
                    proj_emb = await embedding_service.get_embedding(proj_text[:1000])
                    # Cosine similarity is usually in [0.4, 0.9] range for related texts; normalize to 0-100
                    raw_sim = cosine_similarity(proj_emb, jd_embedding)
                    # Scale: raw similarity > 0.75 is exceptional, 0.5 is baseline
                    sim_score = max(0.0, min(100.0, (raw_sim - 0.3) / 0.55 * 100.0))
                except Exception as emb_err:
                    logger.debug(f"Error computing project embedding: {emb_err}")
                    sim_score = lexical_jaccard_similarity(proj_text, combined_jd_text) * 100.0
            else:
                # Lexical Jaccard fallback
                lex_sim = lexical_jaccard_similarity(proj_text, combined_jd_text)
                # Tech overlap bonus
                proj_tech_canon = {t.lower() for t in proj.technologies}
                jd_req_canon = {s.lower() for s in job.required_skills + job.preferred_skills}
                tech_overlap = len(proj_tech_canon.intersection(jd_req_canon)) / max(1, len(jd_req_canon))
                sim_score = min(100.0, (lex_sim * 40.0) + (tech_overlap * 60.0))

            # Identify matching themes / tech
            matched_tech = [t for t in proj.technologies if any(t.lower() == req.lower() for req in job.required_skills + job.preferred_skills)]

            item = ProjectRelevanceItem(
                project_name=proj.name,
                similarity_score=round(sim_score, 1),
                matched_themes=matched_tech,
            )
            items.append(item)
            project_scores.append(sim_score)

        # Aggregate: weight top project most heavily + average of remainder
        if not project_scores:
            return 30.0, []

        sorted_scores = sorted(project_scores, reverse=True)
        top_score = sorted_scores[0]
        avg_score = sum(sorted_scores) / len(sorted_scores)
        composite_score = (top_score * 0.7) + (avg_score * 0.3)
        bounded_score = round(max(0.0, min(100.0, composite_score)), 1)

        return bounded_score, items

    @classmethod
    def evaluate_projects_sync(
        cls,
        resume: ResumeProfile,
        job: JobProfile,
    ) -> Tuple[float, List[ProjectRelevanceItem]]:
        """
        Synchronous project relevance evaluation using lexical overlap and tech matching.
        """
        projects: List[ProjectItem] = resume.projects
        if not projects:
            return 30.0, []

        jd_targets = []
        if job.responsibilities:
            jd_targets.extend(job.responsibilities)
        if job.required_skills:
            jd_targets.append(f"Required skills: {', '.join(job.required_skills)}")
        if job.preferred_skills:
            jd_targets.append(f"Preferred skills: {', '.join(job.preferred_skills)}")
        if job.domain_knowledge:
            jd_targets.append(f"Domain: {', '.join(job.domain_knowledge)}")

        combined_jd_text = " ".join(jd_targets) if jd_targets else f"{job.title} at {job.company}"

        items: List[ProjectRelevanceItem] = []
        project_scores: List[float] = []

        for proj in projects:
            proj_text = f"{proj.name}. {proj.description}. Technologies: {', '.join(proj.technologies)}"
            lex_sim = lexical_jaccard_similarity(proj_text, combined_jd_text)
            proj_tech_canon = {t.lower() for t in proj.technologies}
            jd_req_canon = {s.lower() for s in job.required_skills + job.preferred_skills}
            tech_overlap = len(proj_tech_canon.intersection(jd_req_canon)) / max(1, len(jd_req_canon))
            sim_score = min(100.0, (lex_sim * 40.0) + (tech_overlap * 60.0))

            matched_tech = [t for t in proj.technologies if any(t.lower() == req.lower() for req in job.required_skills + job.preferred_skills)]

            items.append(ProjectRelevanceItem(
                project_name=proj.name,
                similarity_score=round(sim_score, 1),
                matched_themes=matched_tech,
            ))
            project_scores.append(sim_score)

        if not project_scores:
            return 30.0, []

        sorted_scores = sorted(project_scores, reverse=True)
        top_score = sorted_scores[0]
        avg_score = sum(sorted_scores) / len(sorted_scores)
        composite_score = (top_score * 0.7) + (avg_score * 0.3)
        return round(max(0.0, min(100.0, composite_score)), 1), items


# Global singleton
project_relevance_service = ProjectRelevanceService()
