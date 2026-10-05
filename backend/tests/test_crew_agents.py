"""
Tests for CrewAI agent construction, local model configuration, and active vs inactive status.
"""

import pytest
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
from app.agents.base import AgentRole
from app.core.config import settings


def test_active_agents_instantiation():
    """Verify that all 5 Phase 4 active agents instantiate properly with role and goals."""
    active_classes = [
        ManagerAgent,
        JDAnalyzerAgent,
        ResumeAnalyzerAgent,
        EvidenceAgent,
        MatchAnalyzerAgent,
    ]

    for cls in active_classes:
        agent = cls()
        assert agent.name is not None
        assert len(agent.goal) > 0
        assert len(agent.backstory) > 0
        assert agent.metadata.llm_model == settings.OLLAMA_MODEL


def test_inactive_agents_raise_not_implemented():
    """Verify that the 4 Phase 5 deferred agents raise NotImplementedError when created."""
    inactive_classes = [
        ResumeOptimizerAgent,
        FactCheckerAgent,
        ATSValidatorAgent,
        InterviewAgent,
    ]

    for cls in inactive_classes:
        agent = cls()
        with pytest.raises(NotImplementedError):
            agent.create_crewai_agent()


def test_agent_local_model_configuration():
    """Verify local Ollama model configuration with zero cloud references."""
    manager = ManagerAgent()
    assert manager.metadata.llm_model == "llama3.2:3b"

    # Confirm zero forbidden cloud keywords in metadata
    for forbidden in ["openai", "anthropic", "gemini", "azure", "claude", "gpt"]:
        assert forbidden not in manager.metadata.llm_model.lower()


def test_active_agent_crewai_creation_mocked():
    """Verify that active agents can construct underlying CrewAI agents with mock LLM."""
    jd = JDAnalyzerAgent()
    mock_llm = "mock_llm_object"
    crewai_agent = jd.create_crewai_agent(llm=mock_llm, verbose=False)
    assert crewai_agent.role == jd.role
    assert len(crewai_agent.tools) == 3
