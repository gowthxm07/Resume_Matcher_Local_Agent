"""
Tests for ResumeOptimizerAgent, proposal generation, and technical specificity enhancement.
"""

import json
import pytest
from app.agents.resume_optimizer import ResumeOptimizerAgent
from app.agents.base import AgentRole
from app.agents.tools import verify_agent_tool_permissions, get_tool_name
from app.agents.tools.optimizer_tools import (
    retrieve_match_analysis_fn,
    retrieve_resume_claims_fn,
    generate_optimization_proposal_fn,
    get_optimizer_tools,
)
from app.schemas.optimization import OptimizationChange, ChangeType


def test_resume_optimizer_instantiation():
    """Verify ResumeOptimizerAgent initializes with proper role, goal, and local configuration."""
    optimizer = ResumeOptimizerAgent()
    assert optimizer.role == AgentRole.RESUME_OPTIMIZER.value
    assert "Resume Optimizer" in optimizer.name
    assert "verified candidate accomplishments" in optimizer.goal
    assert optimizer.metadata.llm_model == "llama3.2:3b"


def test_resume_optimizer_tool_permissions():
    """Verify ResumeOptimizerAgent has strictly permitted tools and zero git write/arbitrary tools."""
    optimizer = ResumeOptimizerAgent()
    tools = optimizer.get_tools()
    tool_names = {get_tool_name(t) for t in tools}

    expected_tools = {
        "retrieve_match_analysis",
        "retrieve_resume_claims",
        "retrieve_skill_evidence",
        "generate_optimization_proposal",
    }
    assert tool_names == expected_tools
    assert verify_agent_tool_permissions(optimizer.role, tools) is True

    # Security check: Optimizer must not have filesystem write or Git tools
    assert "scan_git_repository" not in tool_names
    assert "execute_shell_command" not in tool_names


def test_generate_optimization_proposal_tool_format():
    """Verify generate_optimization_proposal formats a valid structured JSON proposal."""
    raw_json = generate_optimization_proposal_fn(
        original_text="Built an AI receptionist",
        section="Experience",
        reason="Enrich with verified Next.js and PostgreSQL technologies",
        change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
        proposed_text="Built a full-stack AI receptionist platform using Next.js and PostgreSQL.",
    )
    data = json.loads(raw_json)
    assert data["original_text"] == "Built an AI receptionist"
    assert "Next.js" in data["proposed_text"]
    assert data["change_type"] == "TECHNICAL_SPECIFICITY"
    assert data["status"] == "PENDING"
    assert "change_id" in data


def test_optimizer_crewai_agent_creation_mocked():
    """Verify underlying CrewAI Agent can be constructed with mock LLM."""
    optimizer = ResumeOptimizerAgent()
    crew_agent = optimizer.create_crewai_agent(llm="mock_llm", verbose=False)
    assert crew_agent.role == optimizer.role
    assert len(crew_agent.tools) == 4
