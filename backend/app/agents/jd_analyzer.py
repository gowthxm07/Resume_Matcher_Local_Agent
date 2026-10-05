"""
JD Analyzer Agent implementation for CareerCrew.
Deconstructs job descriptions into hard skills, soft skills, seniority indicators,
domain-specific terminology, and core company expectations.
Uses strictly deterministic tools for requirement classification and skill normalization.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.jd_tools import get_jd_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class JDAnalyzerAgent(BaseCareerAgent):
    """
    JD Analyzer Agent.
    Inspects JobProfile, identifies critical requirements, summarizes required vs preferred skills,
    and isolates high-risk requirements. Strictly isolated from repository scanning or score calculation.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.JD_ANALYZER,
                name="Job Description Requirements Specialist",
                goal="Extract structured requirements, technical competencies, and role expectations from JDs.",
                backstory=(
                    "A veteran tech talent sourcer skilled at reverse-engineering complex job descriptions "
                    "to reveal exact hiring team priorities and critical keyword requirements."
                ),
                planned_tools=["extract_technical_skills", "rank_requirement_weights", "identify_domain_jargon"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return strictly permitted tools for JDAnalyzerAgent."""
        return get_jd_tools()

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
