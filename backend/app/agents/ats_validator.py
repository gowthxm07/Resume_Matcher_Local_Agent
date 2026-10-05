"""
ATS Validator Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class ATSValidatorAgent(BaseCareerAgent):
    """
    ATS Validator Agent (Planned Phase 2 Component).
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
                planned_tools=["simulate_ats_parser", "audit_section_hierarchy", "check_keyword_density"],
                is_implemented=False,
                phase=2,
            )
        )
