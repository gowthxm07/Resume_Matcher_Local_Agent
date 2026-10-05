"""
Manager Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class ManagerAgent(BaseCareerAgent):
    """
    Manager Agent (Planned Phase 2 Component).
    Coordinates the execution order of sub-agents, delegates tasks,
    monitors convergence in iterative optimization loops, and produces final application packages.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.MANAGER,
                name="CareerCrew Chief Orchestrator",
                goal="Coordinate specialized career agents to optimize resume alignment without hallucination.",
                backstory=(
                    "An elite executive talent director and technical recruiter with 15+ years of experience "
                    "guiding candidates to high-impact career matches while upholding the highest ethical standards."
                ),
                planned_tools=["delegate_task", "evaluate_convergence", "compile_final_dossier"],
                is_implemented=False,
                phase=2,
            )
        )
