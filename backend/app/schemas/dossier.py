"""
Pydantic v2 schemas for CrewAI multi-agent outputs, telemetry, and final analysis dossier.
Provides strict validation and error recovery for agent responses.
"""

import re
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, TypeVar, Type
from pydantic import BaseModel, Field, ConfigDict, ValidationError
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Resilient JSON extractor that parses JSON objects from text, stripping fences and repairing syntax."""
    if not text or not text.strip():
        return None
    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            cleaned_candidate = re.sub(r",\s*([\}\]])", r"\1", candidate)
            try:
                return json.loads(cleaned_candidate)
            except json.JSONDecodeError:
                pass
    return None


def safe_utc_now_iso() -> str:
    """Return ISO format string of current UTC time."""
    return datetime.now(timezone.utc).isoformat()


class JDAnalysisOutput(BaseModel):
    """Structured output from JD Analyzer Agent."""
    model_config = ConfigDict(extra="ignore")

    job_title: str = Field(default="Target Role", description="Target role title")
    critical_requirements: List[str] = Field(default_factory=list, description="Non-negotiable required qualifications")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory technical & functional skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or preferred bonus skills")
    min_experience_years: Optional[float] = Field(default=0.0, description="Minimum required years of professional experience")
    high_risk_requirements: List[str] = Field(default_factory=list, description="Rare, difficult, or strict domain-specific requirements")
    key_responsibilities: List[str] = Field(default_factory=list, description="Primary duties and ownership areas")
    analysis_summary: str = Field(default="", description="Executive summary of the job description expectations")


class ResumeAnalysisOutput(BaseModel):
    """Structured output from Resume Analyzer Agent."""
    model_config = ConfigDict(extra="ignore")

    candidate_name: Optional[str] = Field(default="Candidate", description="Name of candidate")
    claimed_technical_skills: List[str] = Field(default_factory=list, description="All technical skills asserted on the resume")
    claimed_experience_years: Optional[float] = Field(default=0.0, description="Total verified years of work experience claimed")
    candidate_strengths: List[str] = Field(default_factory=list, description="Key candidate competencies and distinctive value adds")
    relevant_projects: List[str] = Field(default_factory=list, description="Projects directly applicable to software engineering")
    potential_gaps: List[str] = Field(default_factory=list, description="Unaddressed requirements or thin experience claims")
    analysis_summary: str = Field(default="", description="Executive summary of candidate profile")


class EvidenceAnalysisOutput(BaseModel):
    """Structured output from Evidence Agent."""
    model_config = ConfigDict(extra="ignore")

    verified_skills: List[str] = Field(default_factory=list, description="Skills backed by verified repository evidence (confidence >= 0.85)")
    likely_skills: List[str] = Field(default_factory=list, description="Skills backed by supporting configurations or dev dependencies (0.65 - 0.84)")
    weak_skills: List[str] = Field(default_factory=list, description="Skills mentioned only in documentation/README (<= 0.45)")
    unverified_skills: List[str] = Field(default_factory=list, description="Claimed skills with no matching evidence found in scanned projects")
    unavailable_skills: List[str] = Field(default_factory=list, description="Skills whose verification could not be evaluated due to missing/unreadable repositories")
    evidence_records_count: int = Field(default=0, description="Total atomic evidence records extracted from repos")
    evidence_confidence_score: float = Field(default=0.0, description="Empirical evidence confidence score [0.0 - 100.0]")
    findings_summary: str = Field(default="", description="Forensic summary of evidence grounding")


class MatchAnalysisOutput(BaseModel):
    """Structured output from Match Analyzer Agent."""
    model_config = ConfigDict(extra="ignore")

    overall_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Grounded composite match score [0.0 - 100.0]")
    dimension_scores: Dict[str, float] = Field(default_factory=dict, description="Component breakdown across 7 dimensions")
    matched_requirements: List[str] = Field(default_factory=list, description="Fully satisfied job requirements")
    partial_requirements: List[str] = Field(default_factory=list, description="Partially matched requirements")
    missing_requirements: List[str] = Field(default_factory=list, description="Unmet job requirements")
    verified_skills: List[str] = Field(default_factory=list, description="Skills verified in repositories")
    unverified_skills: List[str] = Field(default_factory=list, description="Skills without repository evidence")
    important_gaps: List[str] = Field(default_factory=list, description="Critical deficiencies against role expectations")
    gap_severity: str = Field(default="LOW", description="Severity classification: LOW, MODERATE, HIGH, CRITICAL")
    analysis_summary: str = Field(default="", description="Synthesis of candidate alignment against target job")


class AgentExecutionTelemetry(BaseModel):
    """Telemetry item recording single agent/task metrics without leaking private resume contents."""
    model_config = ConfigDict(extra="ignore")

    agent_name: str
    task_name: str
    start_time: str
    end_time: str
    duration_ms: float
    llm_invocations: int = 0
    tool_invocations: int = 0
    status: str = "completed"  # completed, failed, skipped
    error: Optional[str] = None


class FinalAnalysisDossier(BaseModel):
    """Unified candidate analysis dossier compiled by Manager Agent."""
    model_config = ConfigDict(extra="ignore")

    analysis_id: str
    resume_id: str
    job_description_id: str
    overall_match_score: float = Field(..., ge=0.0, le=100.0)
    evidence_confidence_score: float = Field(default=0.0, ge=0.0, le=100.0)
    classification: str = Field(default="POTENTIAL_FIT", description="STRONG_FIT, POTENTIAL_FIT, WEAK_FIT, NOT_RECOMMENDED")
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    critical_requirements: List[str] = Field(default_factory=list)
    strong_matches: List[str] = Field(default_factory=list)
    partial_matches: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    verified_skills: List[str] = Field(default_factory=list)
    unverified_skills: List[str] = Field(default_factory=list)
    project_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_gaps: List[str] = Field(default_factory=list)
    agent_execution_summary: Dict[str, Any] = Field(default_factory=dict)
    timing_information: Dict[str, float] = Field(default_factory=dict)
    created_at: str = Field(default_factory=safe_utc_now_iso)

    @property
    def telemetry(self) -> List[Dict[str, Any]]:
        """Return list of agent telemetry entries from execution summary."""
        return self.agent_execution_summary.get("telemetry", [])


class CrewAnalysisRequest(BaseModel):
    """API payload to initiate full CrewAI multi-agent analysis."""
    resume_id: Optional[str] = None
    job_description_id: Optional[str] = None
    project_ids: List[str] = Field(default_factory=list)
    raw_resume_text: Optional[str] = None
    raw_jd_text: Optional[str] = None
    use_live_llm: bool = True


class CrewAnalysisResponse(BaseModel):
    """API response from CrewAI multi-agent analysis."""
    run_id: str
    dossier: FinalAnalysisDossier
    execution_mode: str = "crew_multi_agent"


class BenchmarkComparisonResult(BaseModel):
    """Comparative benchmarking results contrasting deterministic baseline vs multi-agent execution."""
    resume_id: str
    job_description_id: str
    baseline_match_score: float
    crew_match_score: float
    evidence_confidence_score: float
    baseline_execution_ms: float
    crew_execution_ms: float
    baseline_llm_calls: int
    crew_llm_calls: int
    baseline_tool_calls: int
    crew_tool_calls: int
    baseline_missing_requirements_count: int
    crew_missing_requirements_count: int
    score_differential: float
    synthesis_insights: List[str] = Field(default_factory=list)


def parse_agent_json_output(raw_text: str, model_cls: Type[T]) -> T:
    """
    Safely extract and validate JSON output against target Pydantic schema.
    Performs markdown code fence stripping and JSON syntax repair.
    Raises ValueError on unrecoverable validation failure.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError(f"Empty raw text received for schema {model_cls.__name__}")

    data = extract_json_from_text(raw_text)
    if data is None:
        # Fallback direct json load if curly braces already formatted
        try:
            data = json.loads(raw_text.strip())
        except Exception as e:
            raise ValueError(f"Failed to extract JSON for schema {model_cls.__name__}: {e}")

    try:
        return model_cls.model_validate(data)
    except ValidationError as ve:
        logger.warning(f"Validation error for {model_cls.__name__}: {ve}")
        raise ValueError(f"Schema validation failed for {model_cls.__name__}: {ve}")
