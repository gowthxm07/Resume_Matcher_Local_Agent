"""
JD Analyzer Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class JDAnalyzerAgent(BaseCareerAgent):
    """
    JD Analyzer Agent (Planned Phase 2 Component).
    Deconstructs job descriptions into hard skills, soft skills, seniority indicators,
    domain-specific terminology, and core company expectations.
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
