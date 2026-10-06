"""
Resume Optimizer Agent implementation for CareerCrew.
Identifies weak bullet points, unmentioned verified skills, and keyword alignment opportunities.
Proposes evidence-grounded modifications without inventing or exaggerating claims.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.optimizer_tools import get_optimizer_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class ResumeOptimizerAgent(BaseCareerAgent):
    """
    Resume Optimizer Agent.
    Enhances bullet points, highlights verified technical achievements, and aligns tone
    with the target job description WITHOUT fabricating or inventing claims.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.RESUME_OPTIMIZER,
                name="Impact-Driven Resume Optimizer",
                goal="Enhance bullet points and framing based strictly on verified candidate accomplishments.",
                backstory=(
                    "A world-class executive resume writer who crafts compelling, metrics-rich accomplishment "
                    "statements that clearly connect past performance to future employer value while never "
                    "inventing unverified claims."
                ),
                planned_tools=["retrieve_match_analysis", "retrieve_resume_claims", "retrieve_skill_evidence", "generate_optimization_proposal"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return strictly permitted tools for ResumeOptimizerAgent."""
        return get_optimizer_tools()

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
