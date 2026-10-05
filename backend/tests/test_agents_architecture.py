"""
Unit tests for CareerCrew multi-agent architecture and agent blueprints.
"""

from app.agents.orchestration import orchestrator
from app.agents.base import AgentRole


def test_agent_registry_count():
    """Verify that all 9 planned specialized agents are registered."""
    agents = orchestrator.get_all_agents()
    assert len(agents) == 9


def test_all_agent_roles_present():
    """Verify presence of all planned agent roles in the architecture."""
    agents = orchestrator.get_all_agents()
    role_names = {a.metadata.role for a in agents}

    expected_roles = {
        AgentRole.MANAGER,
        AgentRole.JD_ANALYZER,
        AgentRole.RESUME_ANALYZER,
        AgentRole.EVIDENCE,
        AgentRole.MATCH_ANALYZER,
        AgentRole.RESUME_OPTIMIZER,
        AgentRole.FACT_CHECKER,
        AgentRole.ATS_VALIDATOR,
        AgentRole.INTERVIEW,
    }

    assert role_names == expected_roles


def test_agents_marked_for_phase_2():
    """Verify that agents are cleanly flagged as Phase 2 components without fake implementations."""
    for agent in orchestrator.get_all_agents():
        assert agent.is_implemented is False
        assert agent.metadata.phase == 2
        assert len(agent.metadata.planned_tools) > 0
        assert len(agent.goal) > 0
        assert len(agent.backstory) > 0


def test_orchestrator_architecture_summary():
    """Verify orchestrator summary exports structured pipeline stages."""
    summary = orchestrator.get_system_architecture_summary()
    assert summary["agent_count"] == 9
    assert len(summary["pipeline_stages"]) == 4
    assert summary["framework"].startswith("CrewAI")
    assert "Strict local-only" in summary["cloud_dependencies"]
