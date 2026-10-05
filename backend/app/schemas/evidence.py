"""
Pydantic schemas for Phase 3 Evidence-Grounded Project Intelligence.
Defines schemas for project registration, Git metadata, atomic evidence records,
skill verifications, and the complete JD -> Resume -> Project -> Evidence chain.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ConfidenceLevel(str, Enum):
    """Hierarchy of evidence confidence."""
    VERIFIED = "VERIFIED"      # Direct implementation/configuration evidence (>= 0.85)
    LIKELY = "LIKELY"          # Multiple supporting signals but not direct proof (0.65 - 0.84)
    WEAK = "WEAK"              # Documentation or indirect evidence only (0.40 - 0.64)
    UNVERIFIED = "UNVERIFIED"  # Resume claim exists but no repo evidence found (< 0.40)


class EvidenceType(str, Enum):
    """Categorization of repository evidence."""
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    SOURCE_CODE = "source_code"
    DATABASE_SCHEMA = "database_schema"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    GIT_HISTORY = "git_history"
    TEST = "test"
    BUILD = "build"
    DEPLOYMENT = "deployment"


class EvidenceItem(BaseModel):
    """Atomic evidence record demonstrating a technical proficiency."""
    id: Optional[str] = None
    project_id: str
    project_name: Optional[str] = None
    technology: str
    canonical_skill: str
    evidence_type: str
    source_file: str
    source_location: Optional[str] = None
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: str = "UNVERIFIED"
    detector: str
    snippet: Optional[str] = None
    created_at: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class ProjectRegisterRequest(BaseModel):
    """Input payload to register a local candidate software project."""
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1, max_length=1024)
    description: Optional[str] = Field(default="", max_length=2000)
    model_config = ConfigDict(extra="ignore")


class GitCommitSummary(BaseModel):
    """Compact structured summary of a Git commit without large diff blobs."""
    commit_hash: str
    date: str
    author: str
    subject: str
    changed_file_count: int = 0
    additions: int = 0
    deletions: int = 0
    changed_files: List[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class GitMetadata(BaseModel):
    """Repository Git metadata extracted by the safe Git scanner."""
    repo_name: str
    is_git_repo: bool
    branch: Optional[str] = None
    head_commit: Optional[str] = None
    commit_count: int = 0
    first_commit_date: Optional[str] = None
    last_commit_date: Optional[str] = None
    remote_url: Optional[str] = None
    author_stats: Dict[str, int] = Field(default_factory=dict)
    recent_commits: List[GitCommitSummary] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class ProjectResponse(BaseModel):
    """Registered project representation with scan metrics."""
    id: str
    name: str
    description: str
    repo_path: str
    status: str
    git_remote: Optional[str] = None
    git_branch: Optional[str] = None
    head_commit: Optional[str] = None
    commit_count: Optional[int] = 0
    last_scanned_at: Optional[str] = None
    evidence_count: int = 0
    detected_technologies: List[str] = Field(default_factory=list)
    created_at: str
    model_config = ConfigDict(extra="ignore")


class SkillVerificationResult(BaseModel):
    """Verification result mapping an asserted resume skill to real repo evidence."""
    skill: str
    canonical_skill: str
    status: str = "UNVERIFIED"  # VERIFIED, LIKELY, WEAK, UNVERIFIED
    confidence: float = 0.0
    projects: List[str] = Field(default_factory=list)
    evidence_count: int = 0
    evidence_records: List[EvidenceItem] = Field(default_factory=list)
    summary: str = ""
    model_config = ConfigDict(extra="ignore")


class EvidenceChainItem(BaseModel):
    """
    Unified representation linking:
    Job Requirement -> Resume Claim -> Project -> Repository Evidence
    """
    requirement: str
    canonical_skill: str
    requirement_type: str = "required"  # required or preferred
    resume_claimed: bool = False
    resume_evidence: Optional[str] = None
    projects_found: List[str] = Field(default_factory=list)
    verification_status: str = "UNVERIFIED"  # VERIFIED, LIKELY, WEAK, UNVERIFIED
    verification_confidence: float = 0.0
    repository_evidence: List[EvidenceItem] = Field(default_factory=list)
    rationale: str = ""
    model_config = ConfigDict(extra="ignore")


class EvidenceAssessment(BaseModel):
    """
    Overall evidence assessment report correlating an entire application
    against all registered local repositories.
    """
    evidence_confidence_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Independent evidence confidence percentage [0.0 - 100.0]"
    )
    verified_skills_count: int = 0
    likely_skills_count: int = 0
    weak_skills_count: int = 0
    unverified_skills_count: int = 0
    evidence_coverage_percentage: float = 0.0
    chain: List[EvidenceChainItem] = Field(default_factory=list)
    scanned_projects_count: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(extra="ignore")
