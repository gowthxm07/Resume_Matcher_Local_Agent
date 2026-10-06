"""
Pydantic v2 schemas for evidence-grounded resume optimization, fact checking,
deterministic ATS validation, and resume versioning.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


def safe_utc_now_iso() -> str:
    """Return ISO format string of current UTC time."""
    return datetime.now(timezone.utc).isoformat()


class ChangeType(str, Enum):
    """Categorization of proposed resume textual modifications."""
    REWORD = "REWORD"
    TECHNICAL_SPECIFICITY = "TECHNICAL_SPECIFICITY"
    KEYWORD_ALIGNMENT = "KEYWORD_ALIGNMENT"
    REORDER = "REORDER"
    REMOVE_IRRELEVANT = "REMOVE_IRRELEVANT"
    CLARIFY = "CLARIFY"
    ACHIEVEMENT_FRAMING = "ACHIEVEMENT_FRAMING"


class ClaimCategory(str, Enum):
    """Ontological classification of factual assertions extracted from resume claims."""
    SKILL = "SKILL"
    TECHNOLOGY = "TECHNOLOGY"
    PROJECT = "PROJECT"
    METRIC = "METRIC"
    ACHIEVEMENT = "ACHIEVEMENT"
    RESPONSIBILITY = "RESPONSIBILITY"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    CERTIFICATION = "CERTIFICATION"
    ROLE = "ROLE"
    DOMAIN = "DOMAIN"


class FactCheckStatus(str, Enum):
    """Strict truth and evidence grounding verification status."""
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


class VersionStatus(str, Enum):
    """Lifecycle status of a resume version snapshot."""
    ORIGINAL = "ORIGINAL"
    CANDIDATE = "CANDIDATE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FINAL = "FINAL"


class FactualClaim(BaseModel):
    """Atomic factual statement extracted from resume content or proposed modifications."""
    model_config = ConfigDict(extra="ignore")

    claim_id: str
    text: str
    category: str = Field(default=ClaimCategory.SKILL.value)
    section: str = Field(default="Experience")
    source: str = Field(default="proposal", description="Source of claim: original_resume, proposal, or repo_evidence")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of supporting EvidenceRecord objects")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: str = Field(default=FactCheckStatus.UNSUPPORTED.value)
    notes: Optional[str] = None


class OptimizationChange(BaseModel):
    """Structured proposal representing a proposed change to a resume bullet or section."""
    model_config = ConfigDict(extra="ignore")

    change_id: str
    section: str = Field(default="Experience")
    original_text: str
    proposed_text: str
    reason: str
    change_type: str = Field(default=ChangeType.TECHNICAL_SPECIFICITY.value)
    evidence_ids: List[str] = Field(default_factory=list)
    related_jd_requirements: List[str] = Field(default_factory=list)
    expected_impact: str = Field(default="")
    claims: List[FactualClaim] = Field(default_factory=list)
    status: str = Field(default="PENDING", description="PENDING, SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED, ACCEPTED, REJECTED")
    rejection_reason: Optional[str] = None


class FactCheckResult(BaseModel):
    """Outcome of fact-checking a single optimization change or set of claims."""
    model_config = ConfigDict(extra="ignore")

    change_id: str
    overall_status: str = Field(default=FactCheckStatus.UNSUPPORTED.value)
    verified_claims: List[FactualClaim] = Field(default_factory=list)
    unsupported_claims: List[FactualClaim] = Field(default_factory=list)
    contradicted_claims: List[FactualClaim] = Field(default_factory=list)
    repaired_text: Optional[str] = None
    notes: str = Field(default="")


class ATSValidationResult(BaseModel):
    """Deterministic Applicant Tracking System (ATS) compatibility assessment."""
    model_config = ConfigDict(extra="ignore")

    overall_ats_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Heuristic composite ATS score [0-100]")
    parseability_score: float = Field(default=0.0, ge=0.0, le=100.0)
    section_structure_score: float = Field(default=0.0, ge=0.0, le=100.0)
    required_skill_coverage_score: float = Field(default=0.0, ge=0.0, le=100.0)
    preferred_skill_coverage_score: float = Field(default=0.0, ge=0.0, le=100.0)
    keyword_distribution_score: float = Field(default=0.0, ge=0.0, le=100.0)
    formatting_safety_score: float = Field(default=0.0, ge=0.0, le=100.0)
    identified_sections: List[str] = Field(default_factory=list)
    missing_standard_sections: List[str] = Field(default_factory=list)
    matched_required_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    matched_preferred_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    detected_stuffing_keywords: List[str] = Field(default_factory=list)
    formatting_hazards: List[str] = Field(default_factory=list)
    is_ats_compliant: bool = Field(default=True)
    disclaimer: str = Field(
        default="CareerCrew's ATS score is an internal heuristic for resume parseability and job-description alignment. It does not guarantee acceptance by any external ATS."
    )


class ResumeVersionSchema(BaseModel):
    """Pydantic representation of a stored resume version snapshot."""
    model_config = ConfigDict(extra="ignore")

    id: str
    resume_id: str
    parent_version_id: Optional[str] = None
    analysis_id: Optional[str] = None
    iteration: int = 0
    content: str
    match_score: Optional[float] = None
    ats_score: Optional[float] = None
    evidence_confidence: Optional[float] = None
    status: str = Field(default=VersionStatus.ORIGINAL.value)
    change_summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=safe_utc_now_iso)


class OptimizationIterationResult(BaseModel):
    """Record of a single optimization iteration attempt."""
    model_config = ConfigDict(extra="ignore")

    iteration: int
    proposals_count: int = 0
    accepted_changes_count: int = 0
    rejected_changes_count: int = 0
    baseline_match_score: float = 0.0
    iteration_match_score: float = 0.0
    baseline_ats_score: float = 0.0
    iteration_ats_score: float = 0.0
    evidence_confidence_score: float = 0.0
    status: str = Field(default="ACCEPTED")  # ACCEPTED, REJECTED, STOPPED
    changes: List[OptimizationChange] = Field(default_factory=list)
    rejected_claims: List[Dict[str, Any]] = Field(default_factory=list)


class OptimizationDossier(BaseModel):
    """Comprehensive dossier compiling end-to-end resume optimization and audit trail."""
    model_config = ConfigDict(extra="ignore")

    analysis_id: str
    resume_id: str
    job_description_id: str
    baseline_version_id: str
    final_version_id: str
    iterations_run: int
    max_iterations: int = 3
    baseline_match_score: float
    final_match_score: float
    baseline_ats_score: float
    final_ats_score: float
    baseline_evidence_confidence: float
    final_evidence_confidence: float
    total_proposed_changes: int
    total_accepted_changes: int
    total_rejected_changes: int
    accepted_changes: List[OptimizationChange] = Field(default_factory=list)
    rejected_changes: List[OptimizationChange] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    ats_validation: ATSValidationResult
    iterations: List[OptimizationIterationResult] = Field(default_factory=list)
    score_improvement: float = 0.0
    ats_improvement: float = 0.0
    disclaimer: str = Field(
        default="CareerCrew's ATS score is an internal heuristic for resume parseability and job-description alignment. It does not guarantee acceptance by any external ATS."
    )
    created_at: str = Field(default_factory=safe_utc_now_iso)


class OptimizeRequest(BaseModel):
    """API payload to initiate evidence-grounded resume optimization."""
    resume_id: Optional[str] = None
    job_description_id: Optional[str] = None
    project_ids: List[str] = Field(default_factory=list)
    max_iterations: int = Field(default=3, ge=1, le=5)
    raw_resume_text: Optional[str] = None
    raw_jd_text: Optional[str] = None
    use_live_llm: bool = False


class OptimizeResponse(BaseModel):
    """API response from resume optimization."""
    run_id: str
    dossier: OptimizationDossier
    final_version: ResumeVersionSchema
    versions: List[ResumeVersionSchema] = Field(default_factory=list)
