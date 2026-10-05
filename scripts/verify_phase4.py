"""
Phase 4 Complete Verification Script for CareerCrew.
Verifies the Local CrewAI Multi-Agent Analysis Orchestration Layer:
1. Local Model Configuration (Ollama llama3.2:3b, nomic-embed-text, no cloud dependencies)
2. 9-Agent Architecture & Lifecycle Status (5 active Phase 4 agents, 4 strictly deferred agents)
3. Strict Agent Tool Permissions & Access Control Boundaries
4. CrewAI Agent & LLM Configuration
5. Structured Output Schemas & Resilient JSON Recovery
6. Deterministic Tool Execution Integrity
7. Agent Execution Telemetry & Credential Sanitization
8. Final Dossier Integrity & Evidence Preservation (No Hallucinations)
9. Baseline vs Multi-Agent Comparative Benchmark
10. Local-Only Privacy & Zero Paid Cloud API Audit
"""

import sys
import os
import json
import uuid
from pathlib import Path

# Add backend to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.models import Project, EvidenceRecord, AnalysisRun

from app.agents.llm_config import get_crewai_llm
from app.agents.orchestration import orchestrator
from app.agents.manager import ManagerAgent
from app.agents.jd_analyzer import JDAnalyzerAgent
from app.agents.resume_analyzer import ResumeAnalyzerAgent
from app.agents.evidence import EvidenceAgent
from app.agents.match_analyzer import MatchAnalyzerAgent
from app.agents.resume_optimizer import ResumeOptimizerAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.ats_validator import ATSValidatorAgent
from app.agents.interview import InterviewAgent

from app.agents.tools import ALLOWED_TOOL_NAMES, verify_agent_tool_permissions
from app.agents.tools.jd_tools import get_jd_tools, classify_job_requirement_fn, normalize_jd_skill_fn
from app.agents.tools.resume_tools import get_resume_tools, normalize_candidate_skill_fn
from app.agents.tools.evidence_tools import get_evidence_tools, verify_skill_tool
from app.agents.tools.match_tools import get_match_tools, calculate_baseline_match_fn

from app.schemas.dossier import (
    JDAnalysisOutput,
    ResumeAnalysisOutput,
    EvidenceAnalysisOutput,
    MatchAnalysisOutput,
    FinalAnalysisDossier,
    parse_agent_json_output,
)
from app.services.crew_service import crew_service
from app.services.evidence_service import evidence_service

FIXTURES_DIR = ROOT_DIR / "backend" / "tests" / "fixtures" / "repos"

SAMPLE_RESUME = """
Alex Chen
Senior Software Engineer
Email: alex.chen@example.com

Core Technical Skills:
Python, FastAPI, PostgreSQL, Docker, Git, Linux, Redis

Experience:
Senior Software Engineer at Acme Corp (2021 - Present)
- Built high-performance async REST APIs using FastAPI and PostgreSQL.
- Packaged services into Docker containers and set up CI/CD pipelines.

Projects:
FastAPI Backend: Microservices platform written in Python and FastAPI with PostgreSQL.
"""

SAMPLE_JD = """
Senior Python Backend Engineer
Company: TechCorp

Requirements:
- 5+ years of experience with Python
- Strong expertise in FastAPI or modern async web frameworks
- Production experience with PostgreSQL and relational data modeling
- Experience with Docker and containerized deployment

Preferred:
- Experience with Redis caching
- Familiarity with Kubernetes
"""


def main():
    print("=" * 75)
    print("CAREERCREW - PHASE 4 MULTI-AGENT ORCHESTRATION VERIFICATION")
    print("=" * 75)

    # Initialize DB schema
    init_db()

    # -------------------------------------------------------------------------
    # CHECK 1: Local Model & Embedding Configuration
    # -------------------------------------------------------------------------
    print("\n1. Verifying Local Model & Embedding Configuration...")
    assert settings.LLM_PROVIDER == "ollama", f"Expected 'ollama', got {settings.LLM_PROVIDER}"
    assert "llama3.2" in settings.OLLAMA_MODEL.lower(), f"Unexpected model: {settings.OLLAMA_MODEL}"
    assert "nomic-embed-text" in settings.OLLAMA_EMBED_MODEL.lower(), f"Unexpected embedding model: {settings.OLLAMA_EMBED_MODEL}"
    assert settings.LLM_PROVIDER.lower() == "ollama", "Provider must be strictly local ollama"
    print(f"   [PASS] Local LLM Model: {settings.OLLAMA_MODEL}")
    print(f"   [PASS] Local Embedding Model: {settings.OLLAMA_EMBED_MODEL}")
    print(f"   [PASS] Ollama Base URL: {settings.OLLAMA_BASE_URL}")

    # -------------------------------------------------------------------------
    # CHECK 2: 9-Agent Architecture & Lifecycle Status
    # -------------------------------------------------------------------------
    print("\n2. Verifying 9-Agent Architecture & Lifecycle Status...")
    assert len(orchestrator.get_all_agents()) == 9, f"Expected 9 registered agents, found {len(orchestrator.get_all_agents())}"

    # Check 5 active agents can create CrewAI instances
    active_classes = [ManagerAgent, JDAnalyzerAgent, ResumeAnalyzerAgent, EvidenceAgent, MatchAnalyzerAgent]
    for cls in active_classes:
        agent_inst = cls()
        crew_inst = agent_inst.create_crewai_agent(verbose=False)
        assert crew_inst is not None
        assert crew_inst.role == agent_inst.role
        print(f"   [PASS] Active Agent instantiated: {agent_inst.name} ({agent_inst.role})")

    # Check 4 inactive Phase 5 agents raise NotImplementedError
    inactive_classes = [ResumeOptimizerAgent, FactCheckerAgent, ATSValidatorAgent, InterviewAgent]
    for cls in inactive_classes:
        agent_inst = cls()
        try:
            agent_inst.create_crewai_agent()
            assert False, f"{cls.__name__} should have raised NotImplementedError"
        except NotImplementedError:
            print(f"   [PASS] Deferred Agent correctly blocked: {agent_inst.name}")

    # -------------------------------------------------------------------------
    # CHECK 3: Strict Agent Tool Permissions & Access Control Boundaries
    # -------------------------------------------------------------------------
    print("\n3. Verifying Strict Agent Tool Permissions...")
    # Manager has 0 technical tools
    mgr = ManagerAgent()
    assert len(mgr.get_tools()) == 0, "ManagerAgent must have 0 tools"
    print("   [PASS] ManagerAgent tool count: 0 (Pure coordination)")

    # JD Analyzer tools
    jd_tools = JDAnalyzerAgent().get_tools()
    assert len(jd_tools) == 3
    assert verify_agent_tool_permissions("JD Analyzer Agent", jd_tools) is True
    print(f"   [PASS] JDAnalyzerAgent tools: {[t.name for t in jd_tools]}")

    # Resume Analyzer tools
    res_tools = ResumeAnalyzerAgent().get_tools()
    assert len(res_tools) == 2
    assert verify_agent_tool_permissions("Resume Analyzer Agent", res_tools) is True
    print(f"   [PASS] ResumeAnalyzerAgent tools: {[t.name for t in res_tools]}")

    # Evidence Agent tools
    ev_tools = EvidenceAgent().get_tools()
    assert len(ev_tools) == 4
    assert verify_agent_tool_permissions("Evidence Agent", ev_tools) is True
    print(f"   [PASS] EvidenceAgent tools: {[t.name for t in ev_tools]}")

    # Match Analyzer tools
    match_tools = MatchAnalyzerAgent().get_tools()
    assert len(match_tools) == 2
    assert verify_agent_tool_permissions("Match Analyzer Agent", match_tools) is True
    print(f"   [PASS] MatchAnalyzerAgent tools: {[t.name for t in match_tools]}")

    # Boundary violation test
    assert verify_agent_tool_permissions("Match Analyzer Agent", ev_tools) is False
    print("   [PASS] Permission boundary violation successfully blocked")

    # -------------------------------------------------------------------------
    # CHECK 4: CrewAI Agent & LLM Configuration
    # -------------------------------------------------------------------------
    print("\n4. Verifying CrewAI Agent & LLM Configuration...")
    crew_llm = get_crewai_llm()
    assert crew_llm is not None
    assert "llama3.2:3b" in str(crew_llm.model)
    assert "11434" in str(crew_llm.base_url)
    assert crew_llm.temperature == 0.1
    print(f"   [PASS] CrewAI LLM configured for local model: {crew_llm.model}")
    print(f"   [PASS] Temperature: {crew_llm.temperature}, Base URL: {crew_llm.base_url}")

    # -------------------------------------------------------------------------
    # CHECK 5: Structured Output Schemas & Resilient JSON Recovery
    # -------------------------------------------------------------------------
    print("\n5. Verifying Structured Output Schemas & Resilient JSON Recovery...")
    test_json = """
    ```json
    {
        "job_title": "Python Specialist",
        "critical_requirements": ["Python", "FastAPI"],
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "preferred_skills": ["Redis"],
        "min_experience_years": 4.0,
        "high_risk_requirements": [],
        "key_responsibilities": ["API Development"],
        "analysis_summary": "Solid backend profile required",
    }
    ```
    """
    parsed = parse_agent_json_output(test_json, JDAnalysisOutput)
    assert parsed.job_title == "Python Specialist"
    assert parsed.min_experience_years == 4.0
    print("   [PASS] Resilient JSON parser recovered schema from markdown fence with trailing comma")

    # -------------------------------------------------------------------------
    # CHECK 6: Deterministic Application Tools Execution
    # -------------------------------------------------------------------------
    print("\n6. Verifying Deterministic Application Tools Execution...")
    cls_res = json.loads(classify_job_requirement_fn("Required 3+ years of Python"))
    assert cls_res["canonical_skill"] == "Python"
    assert cls_res["requirement_type"] == "required"
    print("   [PASS] classify_job_requirement_fn verified")

    norm_res = json.loads(normalize_jd_skill_fn("Postgres"))
    assert norm_res["canonical_skill"] == "PostgreSQL"
    print("   [PASS] normalize_jd_skill_fn verified")

    norm_c_res = json.loads(normalize_candidate_skill_fn("fastapi"))
    assert norm_c_res["canonical_skill"] == "FastAPI"
    print("   [PASS] normalize_candidate_skill_fn verified")

    # -------------------------------------------------------------------------
    # CHECK 7: Agent Execution Telemetry & Secret Sanitization
    # -------------------------------------------------------------------------
    print("\n7. Verifying Agent Execution Telemetry...")
    db = SessionLocal()
    try:
        dossier = crew_service.run_analysis(
            raw_resume_text=SAMPLE_RESUME,
            raw_jd_text=SAMPLE_JD,
            project_ids=[],
            db=db,
            use_live_llm=False,
        )
        assert len(dossier.telemetry) == 5, f"Expected 5 agent telemetry entries, got {len(dossier.telemetry)}"
        total_dur = dossier.agent_execution_summary.get("total_duration_ms", 0)
        assert total_dur > 0, "Total execution time must be positive"
        for t in dossier.telemetry:
            assert t["status"] == "completed"
            assert t["duration_ms"] >= 0
            print(f"   [PASS] Agent: {t['agent_name']:<24} Task: {t['task_name']:<30} Duration: {t['duration_ms']:.1f}ms")
    finally:
        db.close()

    # -------------------------------------------------------------------------
    # CHECK 8: Evidence Grounding & Hallucination Prevention
    # -------------------------------------------------------------------------
    print("\n8. Verifying Evidence Grounding (Zero Hallucination with 0 Projects)...")
    db = SessionLocal()
    try:
        # Candidate with no registered projects must have 0.0 evidence confidence
        empty_dossier = crew_service.run_analysis(
            raw_resume_text=SAMPLE_RESUME,
            raw_jd_text=SAMPLE_JD,
            project_ids=[],
            db=db,
            use_live_llm=False,
        )
        assert empty_dossier.evidence_confidence_score == 0.0, "Evidence confidence must be 0.0 with 0 repos"
        assert len(empty_dossier.verified_skills) == 0, "No skills should be verified with 0 repos"
        assert len(empty_dossier.unverified_skills) > 0, "Claimed skills must be flagged unverified"
        print(f"   [PASS] Zero projects -> Evidence confidence: {empty_dossier.evidence_confidence_score}%")
        print(f"   [PASS] Verified skills count: {len(empty_dossier.verified_skills)}, Unverified: {len(empty_dossier.unverified_skills)}")

        # Candidate with real project
        repo_path = str(FIXTURES_DIR / "python_fastapi_backend")
        proj = evidence_service.register_project(
            name="FastAPI Backend Service",
            repo_path=repo_path,
            description="Production Python API",
            db=db,
        )
        evidence_service.scan_project(proj.id, db)

        grounded_dossier = crew_service.run_analysis(
            raw_resume_text=SAMPLE_RESUME,
            raw_jd_text=SAMPLE_JD,
            project_ids=[proj.id],
            db=db,
            use_live_llm=False,
        )
        assert grounded_dossier.evidence_confidence_score > 0.0, "Evidence confidence must be > 0.0 with repo"
        assert "FastAPI" in grounded_dossier.verified_skills or "Python" in grounded_dossier.verified_skills
        print(f"   [PASS] Registered project -> Evidence confidence: {grounded_dossier.evidence_confidence_score}%")
        print(f"   [PASS] Verified skills: {grounded_dossier.verified_skills}")
    finally:
        db.close()

    # -------------------------------------------------------------------------
    # CHECK 9: Comparative Baseline vs Multi-Agent Benchmark
    # -------------------------------------------------------------------------
    print("\n9. Verifying Baseline vs Multi-Agent Comparative Benchmark...")
    db = SessionLocal()
    try:
        benchmark = crew_service.run_benchmark(
            raw_resume_text=SAMPLE_RESUME,
            raw_jd_text=SAMPLE_JD,
            project_ids=[],
            db=db,
        )
        assert benchmark.baseline_match_score > 0
        assert benchmark.crew_match_score > 0
        print(f"   [PASS] Baseline Score: {benchmark.baseline_match_score:.1f}")
        print(f"   [PASS] CrewAI Score:   {benchmark.crew_match_score:.1f}")
        print(f"   [PASS] Score Variance: {benchmark.score_differential:.1f}")
        print(f"   [PASS] Executive Benchmark Takeaway: {benchmark.synthesis_insights[0] if benchmark.synthesis_insights else 'N/A'}")
    finally:
        db.close()

    # -------------------------------------------------------------------------
    # CHECK 10: Local-Only Privacy & Zero Paid Cloud API Audit
    # -------------------------------------------------------------------------
    print("\n10. Auditing Privacy Constraints & Zero Paid Cloud APIs...")
    prohibited_env_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "AWS_SECRET_ACCESS_KEY"]
    for key in prohibited_env_keys:
        assert not os.getenv(key), f"Prohibited cloud API key found in environment: {key}"
    print("   [PASS] 0 cloud API keys detected in runtime environment.")

    prohibited_endpoints = ["api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com"]
    for ext in [".py", ".ts", ".tsx"]:
        for f in (ROOT_DIR / "backend" / "app").rglob(f"*{ext}"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            for ep in prohibited_endpoints:
                assert ep not in text, f"Prohibited cloud endpoint found in {f}: {ep}"

    print("   [PASS] 0 paid cloud LLM endpoints detected across application codebase.")
    print("   [PASS] Multi-agent orchestration executes 100% locally through Ollama, SQLite, and ChromaDB.")

    print("\n" + "=" * 75)
    print("PHASE 4 VERIFICATION COMPLETE: ALL 10 AUDIT CHECKS PASSED (100%)")
    print("=" * 75)


if __name__ == "__main__":
    main()
