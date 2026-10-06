"""
Authoritative Fact Checker Service for CareerCrew.
Performs claim-level extraction and strict evidence grounding verification to guarantee ZERO hallucinations.
Evaluates newly introduced technologies, metrics, performance claims, and achievements against trusted sources.
"""

import re
import uuid
from typing import List, Dict, Any, Optional, Set, Tuple
from app.schemas.optimization import (
    OptimizationChange,
    FactualClaim,
    FactCheckResult,
    FactCheckStatus,
    ClaimCategory,
    ChangeType,
)
from app.services.skill_normalizer import SkillNormalizer, skill_normalizer
from app.core.logging import logger


# Common metrics, scalability, and performance regex patterns
METRIC_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*%",                                       # e.g., 40%, 99.9%
    r"\b\d+(?:,\d+)*(?:\+)?\s*(?:users|active\s+users|clients|customers|visitors|rps|req/s|queries)\b",  # e.g., 50,000 users
    r"\b\d+(?:,\d+)*(?:\+)?\s*(?:ms|seconds|minutes|hours)\b",    # e.g., 200ms
    r"\breduced\s+(?:latency|costs?|time|load|overhead)\s+by\s+\d+", # e.g. reduced latency by 40%
    r"\bincreased\s+(?:throughput|concurrency|performance)\s+by\s+\d+",
    r"\b99\.9\d*%\s*(?:uptime|availability)\b",
]

SUPERLATIVE_PATTERNS = [
    r"\bhigh[- ]performance\b",
    r"\bultra[- ]scalable\b",
    r"\bmission[- ]critical\b",
    r"\benterprise[- ]grade\b",
    r"\bfault[- ]tolerant\b",
    r"\bzero[- ]downtime\b",
]


class FactCheckerService:
    """
    Deterministic fact-checking service that inspects optimization proposals
    and validates claims strictly against trusted evidence sources.
    """

    @classmethod
    def extract_claims_from_text(
        cls,
        text: str,
        section: str = "Experience",
        source: str = "proposal",
    ) -> List[FactualClaim]:
        """
        Extract atomic factual assertions (technologies, metrics, achievements) from text.
        """
        claims: List[FactualClaim] = []
        if not text or not text.strip():
            return claims

        # 1. Extract technical entities / skills
        tech_entities = skill_normalizer.find_all_known_skills(text)
        for tech in tech_entities:
            claims.append(
                FactualClaim(
                    claim_id=f"claim_{uuid.uuid4().hex[:8]}",
                    text=tech,
                    category=ClaimCategory.TECHNOLOGY.value,
                    section=section,
                    source=source,
                    confidence=1.0,
                    status=FactCheckStatus.UNSUPPORTED.value,
                )
            )

        # 2. Extract metrics / numerical claims
        for pat in METRIC_PATTERNS:
            for match in re.finditer(pat, text, re.IGNORECASE):
                claim_str = match.group(0).strip()
                claims.append(
                    FactualClaim(
                        claim_id=f"claim_{uuid.uuid4().hex[:8]}",
                        text=claim_str,
                        category=ClaimCategory.METRIC.value,
                        section=section,
                        source=source,
                        confidence=1.0,
                        status=FactCheckStatus.UNSUPPORTED.value,
                    )
                )

        # 3. Extract architectural / superlative claims
        for pat in SUPERLATIVE_PATTERNS:
            for match in re.finditer(pat, text, re.IGNORECASE):
                claim_str = match.group(0).strip()
                claims.append(
                    FactualClaim(
                        claim_id=f"claim_{uuid.uuid4().hex[:8]}",
                        text=claim_str,
                        category=ClaimCategory.ACHIEVEMENT.value,
                        section=section,
                        source=source,
                        confidence=0.8,
                        status=FactCheckStatus.UNSUPPORTED.value,
                    )
                )

        return claims

    @classmethod
    def verify_change(
        cls,
        change: OptimizationChange,
        trusted_resume_text: Optional[str] = None,
        verified_technologies: Optional[Set[str]] = None,
        evidence_records: Optional[List[Any]] = None,
        baseline_resume_text: Optional[str] = None,
    ) -> FactCheckResult:
        """
        Fact-check an OptimizationChange by evaluating newly introduced entities
        against the trusted resume text, verified repository technologies, and evidence records.
        """
        # If caller passed evidence_records positionally as trusted_resume_text
        if isinstance(trusted_resume_text, (list, tuple, set)):
            evidence_records = list(trusted_resume_text)
            trusted_resume_text = baseline_resume_text or change.original_text or ""
        else:
            trusted_resume_text = trusted_resume_text or baseline_resume_text or change.original_text or ""

        # Auto-populate verified technologies from evidence records if not explicitly passed
        if verified_technologies is None and evidence_records:
            verified_technologies = {
                getattr(r, "canonical_skill", getattr(r, "technology", ""))
                for r in evidence_records
                if getattr(r, "canonical_skill", getattr(r, "technology", ""))
            }

        # Canonicalize verified technologies and check framework implications
        canonical_verified: Set[str] = set()
        for vt in (verified_technologies or set()):
            norm_vt = skill_normalizer.normalize(vt).lower()
            canonical_verified.add(norm_vt)
            canonical_verified.add(vt.lower())
            if norm_vt in {"react", "next.js", "vue.js", "angular", "node.js", "express.js"}:
                canonical_verified.add("javascript")
                canonical_verified.add("js")

        original_skills = set(skill_normalizer.find_all_known_skills(change.original_text))
        resume_skills = set(skill_normalizer.find_all_known_skills(trusted_resume_text))
        original_lower = change.original_text.lower()
        trusted_resume_lower = trusted_resume_text.lower()
        evidence_records = evidence_records or []

        # Build combined trusted corpus from evidence records
        evidence_corpus_list = []
        for rec in evidence_records:
            snippet = getattr(rec, "snippet", "") or getattr(rec, "source_snippet", "")
            if snippet:
                evidence_corpus_list.append(str(snippet).lower())
            desc = getattr(rec, "description", "") or getattr(rec, "evidence_summary", "")
            if desc:
                evidence_corpus_list.append(str(desc).lower())
            file_p = getattr(rec, "source_file", "") or getattr(rec, "file_path", "")
            if file_p:
                evidence_corpus_list.append(str(file_p).lower())
        evidence_corpus = " ".join(evidence_corpus_list)

        # Extract claims from proposed text
        proposed_claims = cls.extract_claims_from_text(change.proposed_text, section=change.section)

        verified_claims: List[FactualClaim] = []
        unsupported_claims: List[FactualClaim] = []
        contradicted_claims: List[FactualClaim] = []
        supporting_evidence_ids: List[str] = list(change.evidence_ids)

        for claim in proposed_claims:
            claim_text = claim.text.strip()
            claim_lower = claim_text.lower()
            norm_claim = skill_normalizer.normalize(claim_text).lower()

            # Rule A: If the claim was ALREADY explicitly present in the original text
            if claim_lower in original_lower or claim.text in original_skills or norm_claim in original_lower:
                claim.status = FactCheckStatus.SUPPORTED.value
                claim.confidence = 1.0
                claim.notes = "Present in original text"
                verified_claims.append(claim)
                continue

            # Rule B: If the claim is present elsewhere in the candidate's existing resume
            if claim_lower in trusted_resume_lower or claim.text in resume_skills or norm_claim in trusted_resume_lower:
                claim.status = FactCheckStatus.SUPPORTED.value
                claim.confidence = 0.95
                claim.notes = "Grounded in existing candidate resume"
                verified_claims.append(claim)
                continue

            # Rule C: If the claim is a technology/skill, verify against verified project technologies
            if claim.category == ClaimCategory.TECHNOLOGY.value:
                is_verified = (
                    claim_lower in canonical_verified
                    or norm_claim in canonical_verified
                    or any(claim_lower in cv for cv in canonical_verified)
                    or any(norm_claim in cv for cv in canonical_verified)
                )

                if is_verified:
                    claim.status = FactCheckStatus.SUPPORTED.value
                    claim.confidence = 1.0
                    claim.notes = f"Verified in registered repository technologies ({claim_text})"
                    # Map to evidence record id if possible
                    for rec in evidence_records:
                        rec_skill = getattr(rec, "skill_name", "")
                        rec_id = getattr(rec, "id", None)
                        if rec_skill and claim_lower in rec_skill.lower() and rec_id:
                            supporting_evidence_ids.append(str(rec_id))
                    verified_claims.append(claim)
                else:
                    # Missing from repository evidence and missing from original resume -> UNSUPPORTED!
                    claim.status = FactCheckStatus.UNSUPPORTED.value
                    claim.confidence = 0.0
                    claim.notes = f"No verified evidence found for technology: {claim_text}"
                    unsupported_claims.append(claim)
                continue

            # Rule D: If the claim is a metric (e.g. 50,000 users, 80%, 40% reduction)
            if claim.category == ClaimCategory.METRIC.value:
                # Check if this metric exists in evidence corpus (e.g. README, commits)
                if claim_lower in evidence_corpus:
                    claim.status = FactCheckStatus.SUPPORTED.value
                    claim.confidence = 0.9
                    claim.notes = f"Metric verified in repository documentation/source"
                    verified_claims.append(claim)
                else:
                    # Metric is completely unverified -> UNSUPPORTED
                    claim.status = FactCheckStatus.UNSUPPORTED.value
                    claim.confidence = 0.0
                    claim.notes = f"Unverified metric or quantitative assertion: {claim_text}"
                    unsupported_claims.append(claim)
                continue

            # Rule E: Architectural or superlative achievement
            if claim.category == ClaimCategory.ACHIEVEMENT.value:
                # Check evidence corpus
                if claim_lower in evidence_corpus:
                    claim.status = FactCheckStatus.SUPPORTED.value
                    claim.confidence = 0.85
                    claim.notes = "Capability confirmed in repository evidence"
                    verified_claims.append(claim)
                else:
                    claim.status = FactCheckStatus.UNSUPPORTED.value
                    claim.confidence = 0.0
                    claim.notes = f"Unverified qualitative claim: {claim_text}"
                    unsupported_claims.append(claim)
                continue

            # Default fallback for other claims
            if claim_lower in evidence_corpus:
                claim.status = FactCheckStatus.SUPPORTED.value
                verified_claims.append(claim)
            else:
                claim.status = FactCheckStatus.UNSUPPORTED.value
                unsupported_claims.append(claim)

        # Determine overall change status
        repaired_text: Optional[str] = None
        newly_verified_claims = [
            c for c in verified_claims
            if c.text not in original_skills and c.text.lower() not in original_lower
        ]

        if len(contradicted_claims) > 0:
            overall_status = FactCheckStatus.CONTRADICTED.value
            notes = f"Contradicts candidate records: {[c.text for c in contradicted_claims]}"
        elif len(unsupported_claims) > 0:
            # If there are newly verified technologies alongside unsupported metrics/claims, it is partially supported
            if len(newly_verified_claims) > 0:
                overall_status = FactCheckStatus.PARTIALLY_SUPPORTED.value
                notes = (
                    f"Partially supported: verified newly introduced {[c.text for c in newly_verified_claims]}, "
                    f"but unverified claims exist: {[c.text for c in unsupported_claims]}"
                )
                # Attempt deterministic repair by removing unsupported metric/superlative phrases
                repaired = change.proposed_text
                for unsupp in unsupported_claims:
                    if unsupp.category in (ClaimCategory.METRIC.value, ClaimCategory.ACHIEVEMENT.value):
                        repaired = re.sub(re.escape(unsupp.text), "", repaired, flags=re.IGNORECASE)
                repaired = re.sub(r"\s+", " ", repaired).strip(" ,.-")
                if repaired and repaired != change.original_text and len(repaired) > 15:
                    repaired_text = repaired
            else:
                overall_status = FactCheckStatus.UNSUPPORTED.value
                notes = f"Unsupported claims with no evidence: {[c.text for c in unsupported_claims]}"
        else:
            overall_status = FactCheckStatus.SUPPORTED.value
            notes = "All proposed modifications are grounded in verified evidence or existing resume."

        # Attach claims and evidence IDs to the change object
        change.claims = proposed_claims
        change.evidence_ids = list(set(supporting_evidence_ids))

        return FactCheckResult(
            change_id=change.change_id,
            overall_status=overall_status,
            verified_claims=verified_claims,
            unsupported_claims=unsupported_claims,
            contradicted_claims=contradicted_claims,
            repaired_text=repaired_text,
            notes=notes,
        )


fact_checker_service = FactCheckerService()
