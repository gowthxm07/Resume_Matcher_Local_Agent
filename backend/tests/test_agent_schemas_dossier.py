"""
Tests for structured agent outputs, dossier schemas, and JSON parsing/recovery.
"""

import pytest
from pydantic import ValidationError
from app.schemas.dossier import (
    JDAnalysisOutput,
    ResumeAnalysisOutput,
    EvidenceAnalysisOutput,
    MatchAnalysisOutput,
    FinalAnalysisDossier,
    AgentExecutionTelemetry,
    BenchmarkComparisonResult,
    parse_agent_json_output,
    extract_json_from_text,
)


def test_jd_analysis_output_schema():
    """Verify JDAnalysisOutput schema validation and defaults."""
    output = JDAnalysisOutput(
        job_title="Senior Backend Engineer",
        critical_requirements=["Python", "PostgreSQL"],
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Docker", "Kubernetes"],
        min_experience_years=5.0,
        high_risk_requirements=["Distributed Systems"],
        key_responsibilities=["Build microservices"],
        analysis_summary="High-priority backend engineering role.",
    )
    assert output.job_title == "Senior Backend Engineer"
    assert len(output.required_skills) == 3
    assert output.min_experience_years == 5.0


def test_resume_analysis_output_schema():
    """Verify ResumeAnalysisOutput schema validation."""
    output = ResumeAnalysisOutput(
        candidate_name="Alex Chen",
        claimed_technical_skills=["Python", "FastAPI", "PostgreSQL"],
        claimed_experience_years=5.5,
        candidate_strengths=["Strong backend API depth"],
        relevant_projects=["Distributed Task Queue"],
        potential_gaps=[],
        analysis_summary="Strong mid/senior backend candidate.",
    )
    assert output.candidate_name == "Alex Chen"
    assert output.claimed_experience_years == 5.5


def test_evidence_analysis_output_distinguishes_unverified_and_unavailable():
    """Verify EvidenceAnalysisOutput explicitly distinguishes UNVERIFIED from UNAVAILABLE."""
    output = EvidenceAnalysisOutput(
        verified_skills=["FastAPI", "PostgreSQL"],
        likely_skills=["Docker"],
        weak_skills=["Kubernetes"],
        unverified_skills=["Redis"],
        unavailable_skills=["Project repo 'proj-99' was unreadable"],
        evidence_records_count=12,
        evidence_confidence_score=75.5,
        findings_summary="Forensic project scan complete.",
    )
    # UNVERIFIED means scanned and no evidence found
    assert "Redis" in output.unverified_skills
    # UNAVAILABLE means repo could not be evaluated due to failure
    assert len(output.unavailable_skills) == 1
    assert "unreadable" in output.unavailable_skills[0]


def test_final_dossier_schema_and_boundaries():
    """Verify FinalAnalysisDossier schema fields and score range constraints."""
    dossier = FinalAnalysisDossier(
        analysis_id="test-run-123",
        resume_id="res-1",
        job_description_id="jd-1",
        overall_match_score=88.5,
        evidence_confidence_score=92.0,
        classification="STRONG_FIT",
        dimension_scores={"required_skills": 90.0, "depth": 85.0},
        critical_requirements=["Python"],
        strong_matches=["Python", "FastAPI"],
        partial_matches=[],
        missing_requirements=[],
        verified_skills=["Python", "FastAPI"],
        unverified_skills=[],
        key_strengths=["Deep Python expertise"],
        key_gaps=[],
    )
    assert dossier.overall_match_score == 88.5
    assert dossier.classification == "STRONG_FIT"

    # Score bounds [0.0 - 100.0] enforcement
    with pytest.raises(ValidationError):
        FinalAnalysisDossier(
            analysis_id="invalid",
            resume_id="res-1",
            job_description_id="jd-1",
            overall_match_score=150.0,  # invalid > 100
            classification="INVALID",
        )


def test_parse_agent_json_output_clean():
    """Verify parsing clean JSON string into target schema."""
    raw = '{"job_title": "Staff Engineer", "required_skills": ["Python", "Rust"], "min_experience_years": 8.0}'
    output = parse_agent_json_output(raw, JDAnalysisOutput)
    assert output.job_title == "Staff Engineer"
    assert len(output.required_skills) == 2
    assert output.min_experience_years == 8.0


def test_parse_agent_json_output_with_markdown_fences():
    """Verify parsing JSON wrapped in markdown ```json code fences."""
    raw = """
    Here is the analysis result:
    ```json
    {
      "candidate_name": "Jane Doe",
      "claimed_technical_skills": ["TypeScript", "React", "Next.js"],
      "claimed_experience_years": 4.0,
      "candidate_strengths": ["Frontend architecture"],
      "relevant_projects": ["E-Commerce UI"],
      "analysis_summary": "Solid frontend engineer."
    }
    ```
    Please review above.
    """
    output = parse_agent_json_output(raw, ResumeAnalysisOutput)
    assert output.candidate_name == "Jane Doe"
    assert "React" in output.claimed_technical_skills


def test_parse_agent_json_output_with_trailing_commas():
    """Verify resilient parser handles trailing commas."""
    raw = """
    {
      "candidate_name": "Bob Smith",
      "claimed_technical_skills": ["Go", "Kubernetes",],
      "claimed_experience_years": 3.0,
    }
    """
    output = parse_agent_json_output(raw, ResumeAnalysisOutput)
    assert output.candidate_name == "Bob Smith"


def test_parse_agent_json_output_malformed_raises_value_error():
    """Verify malformed unrecoverable text raises ValueError with clear message."""
    raw = "This is just plain text without any JSON content."
    with pytest.raises(ValueError) as exc_info:
        parse_agent_json_output(raw, JDAnalysisOutput)
    assert "Failed to extract JSON" in str(exc_info.value) or "Schema validation failed" in str(exc_info.value)


def test_benchmark_comparison_schema():
    """Verify BenchmarkComparisonResult schema."""
    bm = BenchmarkComparisonResult(
        resume_id="res-1",
        job_description_id="jd-1",
        baseline_match_score=85.0,
        crew_match_score=85.0,
        evidence_confidence_score=80.0,
        baseline_execution_ms=120.5,
        crew_execution_ms=350.0,
        baseline_llm_calls=0,
        crew_llm_calls=5,
        baseline_tool_calls=1,
        crew_tool_calls=8,
        baseline_missing_requirements_count=1,
        crew_missing_requirements_count=1,
        score_differential=0.0,
        synthesis_insights=["Score is 100% consistent with baseline."],
    )
    assert bm.score_differential == 0.0
    assert bm.baseline_match_score == 85.0
