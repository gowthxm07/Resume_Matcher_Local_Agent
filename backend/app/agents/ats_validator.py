"""
ATS Validator Agent implementation for CareerCrew.
Simulates applicant tracking systems to evaluate machine parseability,
section hierarchy, keyword density, and formatting compliance.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.ats_tools import get_ats_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class ATSValidatorAgent(BaseCareerAgent):
    """
    ATS Validator Agent.
    Simulates modern Applicant Tracking System parsers (Taleo, Greenhouse, Lever, Workday)
    to verify machine parseability, keyword placement, and heading standardization.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.ATS_VALIDATOR,
                name="Applicant Tracking System Emulator",
                goal="Ensure optimal machine parseability, section hierarchy, and keyword density for ATS filters.",
                backstory=(
                    "An enterprise HR systems engineer who has built and tuned ATS parsing engines "
                    "and knows precisely how automated filters interpret structured candidate documents."
                ),
                planned_tools=[
                    "validate_resume_structure",
                    "calculate_keyword_coverage",
                    "validate_parseability",
                    "detect_keyword_stuffing",
                    "calculate_ats_score",
                ],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return strictly permitted tools for ATSValidatorAgent."""
        return get_ats_tools()

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
