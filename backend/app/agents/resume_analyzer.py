"""
Resume Analyzer Agent implementation for CareerCrew.
Deconstructs candidate resumes into chronological experience, claimed competencies,
distinctive strengths, and quantifiable achievements.
Uses strictly deterministic tools for skill normalization and category classification.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.resume_tools import get_resume_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class ResumeAnalyzerAgent(BaseCareerAgent):
    """
    Resume Analyzer Agent.
    Inspects ResumeProfile, isolates claimed skills, projects, and strengths.
    Strictly isolated from repository scanning or score calculation. Never modifies resume.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.RESUME_ANALYZER,
                name="Candidate Resume Deconstructor",
                goal="Parse and structure candidate experience, asserted skills, and quantifiable achievements.",
                backstory=(
                    "A meticulous resume auditor who reads between the lines of candidate CVs, "
                    "extracting precise accomplishments, metrics, and technological proficiencies."
                ),
                planned_tools=["extract_work_history", "extract_claimed_skills", "parse_bullet_metrics"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return strictly permitted tools for ResumeAnalyzerAgent."""
        return get_resume_tools()

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
