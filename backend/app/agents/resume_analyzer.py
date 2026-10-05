"""
Resume Analyzer Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class ResumeAnalyzerAgent(BaseCareerAgent):
    """
    Resume Analyzer Agent (Planned Phase 2 Component).
    Parses candidate resumes into chronological experience blocks, bullet points,
    explicit skill assertions, metrics, and academic/credential histories.
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
