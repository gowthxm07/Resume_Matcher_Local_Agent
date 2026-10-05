"""
Resume Optimizer Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class ResumeOptimizerAgent(BaseCareerAgent):
    """
    Resume Optimizer Agent (Planned Phase 2 Component).
    Rewrites bullet points, highlights verified accomplishments, and aligns tone
    with the target job description WITHOUT fabricating or exaggerating claims.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.RESUME_OPTIMIZER,
                name="Impact-Driven Resume Optimizer",
                goal="Enhance bullet points and framing based strictly on verified candidate accomplishments.",
                backstory=(
                    "A world-class executive resume writer who crafts compelling, metrics-rich accomplishment "
                    "statements that clearly connect past performance to future employer value."
                ),
                planned_tools=["refactor_bullet_xyz_format", "inject_verified_evidence", "align_tone"],
                is_implemented=False,
                phase=2,
            )
        )
