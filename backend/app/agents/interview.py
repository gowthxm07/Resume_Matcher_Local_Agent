"""
Interview Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class InterviewAgent(BaseCareerAgent):
    """
    Interview Agent (Planned Phase 2 Component).
    Generates targeted technical deep-dives, system architecture challenges, and STAR-format
    behavioral questions directly grounded in the candidate's real project evidence and target role.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.INTERVIEW,
                name="Technical & Behavioral Interview Prep Coach",
                goal="Generate deep-dive technical and STAR interview questions grounded in candidate's verified evidence.",
                backstory=(
                    "A distinguished engineering director and bar-raiser interviewer who crafts probing "
                    "scenario-based technical and behavioral questions tailored to candidate experiences."
                ),
                planned_tools=["generate_technical_questions", "generate_star_scenarios", "evaluate_mock_answers"],
                is_implemented=False,
                phase=2,
            )
        )

    def create_crewai_agent(self, llm=None, verbose: bool = False):
        """InterviewAgent is deferred to future phase."""
        raise NotImplementedError(
            "InterviewAgent is strictly deferred to future phase."
        )
