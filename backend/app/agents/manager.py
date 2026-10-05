"""
Manager Agent orchestration coordinator for CareerCrew.
Coordinates workflow execution, validates agent inputs, collects structured findings,
and compiles the FinalAnalysisDossier without independently computing technical scores.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class ManagerAgent(BaseCareerAgent):
    """
    Manager Agent (Chief Orchestrator).
    Coordinates execution order of specialist agents, maintains execution context,
    ensures required tasks are completed, and compiles the final AnalysisDossier.
    Maintains zero direct technical scoring tools.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.MANAGER,
                name="CareerCrew Chief Orchestrator",
                goal="Coordinate specialized career agents to synthesize resume and job intelligence into an explainable dossier.",
                backstory=(
                    "An elite executive talent director and technical recruiter with 15+ years of experience "
                    "guiding candidates to high-impact career matches while upholding the highest ethical standards."
                ),
                planned_tools=["delegate_task", "evaluate_convergence", "compile_final_dossier"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Manager agent has zero technical tools (orchestration and synthesis only)."""
        return []

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
