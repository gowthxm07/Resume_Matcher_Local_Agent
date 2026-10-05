"""
Match Analyzer Agent implementation for CareerCrew.
Assesses factual alignment between candidate skills and job requirements, identifying coverage gaps.
Invokes deterministic Phase 2 matching engine for authoritative baseline scoring.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.match_tools import get_match_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class MatchAnalyzerAgent(BaseCareerAgent):
    """
    Match Analyzer Agent.
    Combines JD analysis, Resume analysis, and Evidence findings.
    Invokes deterministic matching engine for score calculation and surfaces critical gaps.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.MATCH_ANALYZER,
                name="Alignment & Gap Auditor",
                goal="Assess factual alignment between candidate skills and job requirements, identifying coverage gaps.",
                backstory=(
                    "An analytical compensation and talent matching strategist who computes objective "
                    "compatibility matrices between candidate abilities and role requirements."
                ),
                planned_tools=["compute_match_score", "identify_coverage_gaps", "rank_priority_alignments"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return strictly permitted tools for MatchAnalyzerAgent."""
        return get_match_tools()

    def create_crewai_agent(self, llm=None, verbose: bool = False):
        """Instantiate underlying CrewAI Agent instance configured with local Ollama."""
        agent_llm = llm or get_crewai_llm()
        if Agent is None:
            raise RuntimeError("CrewAI Agent class is not installed.")
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.get_tools(),
            llm=agent_llm,
            verbose=verbose,
            allow_delegation=False,
        )
