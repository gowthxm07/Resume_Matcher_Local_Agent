"""
Fact Checker Agent implementation for CareerCrew.
Primary anti-hallucination guardrail that cross-references all proposed resume modifications
against the original resume and verified project evidence to guarantee ZERO hallucinations.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.fact_checker_tools import get_fact_checker_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class FactCheckerAgent(BaseCareerAgent):
    """
    Fact Checker Agent.
    Rigorous verification guardrail that cross-references all rewritten resume bullets
    against the original resume and verified project evidence to guarantee ZERO hallucinations.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.FACT_CHECKER,
                name="Strict Truth & Hallucination Auditor",
                goal="Guarantee absolute fidelity to truth by detecting and rejecting any unverified or fabricated claim.",
                backstory=(
                    "An unyielding background investigation and compliance auditor who verifies that "
                    "every claim, metric, and skill is mathematically grounded in verifiable source material."
                ),
                planned_tools=["retrieve_claim", "retrieve_evidence", "verify_skill", "compare_claim_evidence"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return strictly permitted tools for FactCheckerAgent."""
        return get_fact_checker_tools()

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
