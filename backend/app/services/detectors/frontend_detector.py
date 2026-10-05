"""
Frontend configuration technology detector.
Inspects next.config.*, vite.config.*, angular.json, and tailwind.config.*.
"""

from pathlib import Path
from typing import List
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer


class FrontendDetector(BaseDetector):
    """Detects frontend meta-frameworks and build tools from config files."""

    name = "frontend_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # Next.js configuration
        for next_cfg in ["next.config.js", "next.config.mjs", "next.config.ts"]:
            p = repo_path / next_cfg
            if p.is_file():
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Next.js",
                        canonical_skill=skill_normalizer.normalize("Next.js"),
                        evidence_type=EvidenceType.CONFIGURATION.value,
                        source_file=next_cfg,
                        description="Next.js application configuration file defined.",
                        confidence=0.99,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )
                break

        # Vite configuration
        for vite_cfg in ["vite.config.js", "vite.config.ts", "vite.config.mjs"]:
            p = repo_path / vite_cfg
            if p.is_file():
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Vite",
                        canonical_skill=skill_normalizer.normalize("Vite"),
                        evidence_type=EvidenceType.BUILD.value,
                        source_file=vite_cfg,
                        description="Vite build bundler configuration file defined.",
                        confidence=0.98,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )
                break

        # Tailwind CSS configuration
        for tw_cfg in ["tailwind.config.js", "tailwind.config.ts", "tailwind.config.mjs"]:
            p = repo_path / tw_cfg
            if p.is_file():
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Tailwind CSS",
                        canonical_skill=skill_normalizer.normalize("Tailwind CSS"),
                        evidence_type=EvidenceType.CONFIGURATION.value,
                        source_file=tw_cfg,
                        description="Tailwind CSS styling configuration defined.",
                        confidence=0.98,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )
                break

        # Angular configuration
        ang_cfg = repo_path / "angular.json"
        if ang_cfg.is_file():
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Angular",
                    canonical_skill=skill_normalizer.normalize("Angular"),
                    evidence_type=EvidenceType.CONFIGURATION.value,
                    source_file="angular.json",
                    description="Angular workspace configuration present.",
                    confidence=0.99,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

        return items
