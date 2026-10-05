"""
Java and JVM ecosystem technology detector.
Inspects Maven pom.xml and Gradle build.gradle files for JVM dependencies.
"""

import re
from pathlib import Path
from typing import List
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer
from app.core.logging import logger


class JavaDetector(BaseDetector):
    """Detects Java, Spring Boot, Maven, and Gradle dependencies."""

    name = "java_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # 1. Maven pom.xml
        pom_file = repo_path / "pom.xml"
        if pom_file.is_file():
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Java",
                    canonical_skill=skill_normalizer.normalize("Java"),
                    evidence_type=EvidenceType.CONFIGURATION.value,
                    source_file="pom.xml",
                    description="Java project defined with Maven build system.",
                    confidence=0.99,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Maven",
                    canonical_skill=skill_normalizer.normalize("Maven"),
                    evidence_type=EvidenceType.BUILD.value,
                    source_file="pom.xml",
                    description="Maven pom.xml build file defined.",
                    confidence=0.98,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

            try:
                content = pom_file.read_text(encoding="utf-8", errors="ignore")
                if "spring-boot" in content:
                    items.append(
                        EvidenceItem(
                            project_id=project_id,
                            technology="Spring Boot",
                            canonical_skill=skill_normalizer.normalize("Spring Boot"),
                            evidence_type=EvidenceType.DEPENDENCY.value,
                            source_file="pom.xml",
                            description="Spring Boot dependency configured in Maven.",
                            confidence=0.98,
                            confidence_level=ConfidenceLevel.VERIFIED.value,
                            detector=self.name,
                        )
                    )
                if "postgresql" in content.lower():
                    items.append(
                        EvidenceItem(
                            project_id=project_id,
                            technology="PostgreSQL",
                            canonical_skill=skill_normalizer.normalize("PostgreSQL"),
                            evidence_type=EvidenceType.DEPENDENCY.value,
                            source_file="pom.xml",
                            description="PostgreSQL JDBC driver configured in Maven.",
                            confidence=0.98,
                            confidence_level=ConfidenceLevel.VERIFIED.value,
                            detector=self.name,
                        )
                    )
            except Exception as exc:
                logger.warning(f"Error parsing pom.xml in '{repo_path}': {exc}")

        # 2. Gradle build.gradle
        for gradle_file in ["build.gradle", "build.gradle.kts"]:
            gf = repo_path / gradle_file
            if gf.is_file():
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Gradle",
                        canonical_skill=skill_normalizer.normalize("Gradle"),
                        evidence_type=EvidenceType.BUILD.value,
                        source_file=gradle_file,
                        description="Gradle project build file present.",
                        confidence=0.98,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Java",
                        canonical_skill=skill_normalizer.normalize("Java"),
                        evidence_type=EvidenceType.CONFIGURATION.value,
                        source_file=gradle_file,
                        description="Java project defined with Gradle build system.",
                        confidence=0.98,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )
                break

        return items
