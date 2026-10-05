"""
Structured Pydantic schemas for Phase 2 intelligence layer.
Defines ResumeProfile, JobProfile, SkillRequirement, MatchClassification,
DimensionScores, and explainable AnalysisResult.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MatchClassification(str, Enum):
    """Classification of how candidate background satisfies a JD requirement."""
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISSING = "MISSING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RequirementType(str, Enum):
    """Distinction between mandatory and optional job requirements."""
    REQUIRED = "required"
    PREFERRED = "preferred"


class SkillCategory(str, Enum):
    """Controlled categories for technical and professional requirements."""
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD = "cloud"
    DEVOPS = "devops"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    DOMAIN = "domain"
    OTHER = "other"


# --- Resume Profile Schemas ---

class ContactMetadata(BaseModel):
    """Candidate contact information extracted from resume."""
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class SkillsInventory(BaseModel):
    """Categorized technical and professional skills asserted in resume."""
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_platforms: List[str] = Field(default_factory=list)
    tools_and_devops: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)

    def all_technical_skills(self) -> List[str]:
        """Aggregate all distinct technical skill strings."""
        skills = []
        for lst in [
            self.programming_languages,
            self.frameworks,
            self.libraries,
            self.databases,
            self.cloud_platforms,
            self.tools_and_devops,
            self.other,
        ]:
            skills.extend(lst)
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for s in skills:
            clean = s.strip()
            if clean and clean.lower() not in seen:
                seen.add(clean.lower())
                deduped.append(clean)
        return deduped

    model_config = ConfigDict(extra="ignore")


class EducationItem(BaseModel):
    """Academic credential listed on resume."""
    institution: str = "Unknown Institution"
    degree: str = "Degree"
    field_of_study: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class WorkExperienceItem(BaseModel):
    """Professional role or internship experience block."""
    organization: str = "Organization"
    role: str = "Role"
    duration: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    measurable_achievements: List[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class ProjectItem(BaseModel):
    """Candidate software project or portfolio codebase."""
    name: str = "Project"
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    measurable_results: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class ResumeProfile(BaseModel):
    """
    Normalized, structured candidate profile parsed from resume documents.
    Does not invent claims; empty sections remain empty lists/None.
    """
    candidate_name: Optional[str] = None
    contact_info: ContactMetadata = Field(default_factory=ContactMetadata)
    summary: Optional[str] = None
    skills: SkillsInventory = Field(default_factory=SkillsInventory)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    internships: List[WorkExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)
    raw_text_hash: Optional[str] = None
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="ignore")


# --- Job Description Profile Schemas ---

class CategorizedRequirement(BaseModel):
    """A single requirement extracted from a job description."""
    canonical_skill: str
    original_text: str
    requirement_type: RequirementType = RequirementType.REQUIRED
    category: SkillCategory = SkillCategory.OTHER
    importance: str = "medium"  # critical, high, medium, low
    min_years: Optional[float] = None
    confidence: float = 1.0
    model_config = ConfigDict(extra="ignore")


class JobProfile(BaseModel):
    """
    Structured representation of a target Job Description.
    Critically separates REQUIRED competencies from PREFERRED competencies.
    """
    title: str = "Target Position"
    company: str = "Company"
    location: Optional[str] = None
    employment_type: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    categorized_requirements: List[CategorizedRequirement] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_technologies: List[str] = Field(default_factory=list)
    developer_tools: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    experience_requirements: List[str] = Field(default_factory=list)
    min_years_experience: Optional[float] = None
    certifications: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    domain_knowledge: List[str] = Field(default_factory=list)
    raw_text_hash: Optional[str] = None
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="ignore")


# --- Match Analysis Schemas ---

class RequirementMatchResult(BaseModel):
    """Granular match assessment for an individual requirement with grounded candidate evidence."""
    requirement: str
    canonical_skill: str
    requirement_type: RequirementType
    category: SkillCategory
    classification: MatchClassification
    candidate_evidence: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    explanation: str = ""
    model_config = ConfigDict(extra="ignore")


class DimensionScores(BaseModel):
    """Detailed dimensional score breakdown (each dimension bounded strictly between 0 and 100)."""
    required_skill_score: float = Field(default=0.0, ge=0.0, le=100.0)
    preferred_skill_score: float = Field(default=0.0, ge=0.0, le=100.0)
    technical_depth_score: float = Field(default=0.0, ge=0.0, le=100.0)
    project_relevance_score: float = Field(default=0.0, ge=0.0, le=100.0)
    experience_alignment_score: float = Field(default=0.0, ge=0.0, le=100.0)
    education_alignment_score: float = Field(default=0.0, ge=0.0, le=100.0)
    keyword_coverage_score: float = Field(default=0.0, ge=0.0, le=100.0)
    model_config = ConfigDict(extra="ignore")


class ProjectRelevanceItem(BaseModel):
    """Semantic relevance evaluation between a candidate project and job requirements."""
    project_name: str
    similarity_score: float = 0.0
    matched_themes: List[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class AnalysisMetadata(BaseModel):
    """Operational telemetry for the analysis run."""
    llm_provider: str = "ollama"
    model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"
    extraction_time_ms: float = 0.0
    inference_time_ms: float = 0.0
    analysis_time_ms: float = 0.0
    total_time_ms: float = 0.0
    cached_resume: bool = False
    cached_jd: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(extra="ignore")


class AnalysisResult(BaseModel):
    """
    Comprehensive explainable match analysis report.
    Produces deterministic, reproducible scores and requirement classifications.
    """
    overall_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Weighted composite match score 0-100")
    dimension_scores: DimensionScores = Field(default_factory=DimensionScores)
    scoring_weights: Dict[str, float] = Field(default_factory=dict)
    requirements_analysis: List[RequirementMatchResult] = Field(default_factory=list)
    matched_requirements: List[RequirementMatchResult] = Field(default_factory=list)
    partial_matches: List[RequirementMatchResult] = Field(default_factory=list)
    missing_requirements: List[RequirementMatchResult] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)
    project_relevance: List[ProjectRelevanceItem] = Field(default_factory=list)
    summary_explanation: str = ""
    resume_id: Optional[str] = None
    job_description_id: Optional[str] = None
    analysis_run_id: Optional[str] = None
    metadata: AnalysisMetadata = Field(default_factory=AnalysisMetadata)
    model_config = ConfigDict(extra="ignore")
