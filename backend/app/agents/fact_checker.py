"""
Fact Checker Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class FactCheckerAgent(BaseCareerAgent):
    """
    Fact Checker Agent (Planned Phase 2 Component).
    Rigorous verification guardrail that cross-references all rewritten resume bullets
    against the original resume and verified project evidence to guarantee ZERO hallucinations.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.FACT_CHECKER,
                name="Strict Truth & Hallucination Auditor",
                goal="Guarantee absolute fidelity to truth by detecting and rejecting any unverified or fabricated claim.",
                backstory=(
                    "An unyielding background investigation and compliance auditor who verifies that "
                    "every claim, metric, and skill is mathematically grounded in verifiable source material."
                ),
                planned_tools=["verify_claim_entailment", "detect_fabricated_metrics", "flag_unverified_skills"],
                is_implemented=False,
                phase=2,
            )
        )
