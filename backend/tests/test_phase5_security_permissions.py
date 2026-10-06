"""
Security and architectural boundary verification for Phase 5.
Validates least-privilege tool execution, InterviewAgent deferral, and 100% local operation.
"""

import pytest
from app.agents.resume_optimizer import ResumeOptimizerAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.ats_validator import ATSValidatorAgent
from app.agents.interview import InterviewAgent
from app.agents.tools import verify_agent_tool_permissions
from app.core.config import settings


def test_phase5_tool_permission_boundaries():
    """Verify that all Phase 5 agents adhere to their authorized tool lists."""
    optimizer = ResumeOptimizerAgent()
    assert verify_agent_tool_permissions(optimizer.role, optimizer.get_tools()) is True

    checker = FactCheckerAgent()
    assert verify_agent_tool_permissions(checker.role, checker.get_tools()) is True

    ats = ATSValidatorAgent()
    assert verify_agent_tool_permissions(ats.role, ats.get_tools()) is True


def test_interview_agent_strictly_deferred():
    """Verify InterviewAgent is strictly deferred and raises NotImplementedError."""
    interview = InterviewAgent()
    with pytest.raises(NotImplementedError):
        interview.create_crewai_agent()


def test_zero_cloud_api_dependencies():
    """Verify zero external cloud LLM or vector APIs are configured in settings."""
    forbidden_cloud_terms = [
        "openai",
        "anthropic",
        "gemini",
        "azure",
        "pinecone",
        "supabase",
        "aws.amazon",
        "claude-",
        "gpt-4",
    ]

    for key, val in settings.__dict__.items():
        if isinstance(val, str):
            for term in forbidden_cloud_terms:
                assert term not in val.lower(), f"Forbidden cloud provider '{term}' detected in {key}={val}"

    assert settings.LLM_PROVIDER == "ollama"
    assert "localhost" in settings.OLLAMA_BASE_URL or "127.0.0.1" in settings.OLLAMA_BASE_URL
