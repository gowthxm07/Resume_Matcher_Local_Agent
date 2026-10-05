"""
JavaScript and TypeScript ecosystem technology detector.
Inspects package.json, tsconfig.json, and lockfiles for genuine dependency evidence.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer
from app.core.logging import logger

# Package name to canonical technology mapping
PACKAGE_MAPPING = {
    "react": ("React", "framework"),
    "react-dom": ("React", "framework"),
    "next": ("Next.js", "framework"),
    "typescript": ("TypeScript", "programming_language"),
    "express": ("Express", "framework"),
    "@nestjs/core": ("NestJS", "framework"),
    "vue": ("Vue.js", "framework"),
    "@angular/core": ("Angular", "framework"),
    "prisma": ("Prisma", "tool"),
    "@prisma/client": ("Prisma", "tool"),
    "pg": ("PostgreSQL", "database"),
    "postgres": ("PostgreSQL", "database"),
    "mysql": ("MySQL", "database"),
    "mysql2": ("MySQL", "database"),
    "mongoose": ("MongoDB", "database"),
    "mongodb": ("MongoDB", "database"),
    "redis": ("Redis", "database"),
    "ioredis": ("Redis", "database"),
    "tailwindcss": ("Tailwind CSS", "framework"),
    "jest": ("Jest", "testing"),
    "vitest": ("Vitest", "testing"),
    "graphql": ("GraphQL", "tool"),
    "redux": ("Redux", "library"),
    "@reduxjs/toolkit": ("Redux", "library"),
    "zod": ("Zod", "library"),
    "axios": ("Axios", "library"),
    "fastify": ("Fastify", "framework"),
    "cypress": ("Cypress", "testing"),
    "playwright": ("Playwright", "testing"),
}


class PackageJsonDetector(BaseDetector):
    """Detects JS/TS dependencies, frameworks, and tools from package.json and tsconfig.json."""

    name = "package_json_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # 1. Inspect package.json
        pkg_file = repo_path / "package.json"
        if pkg_file.is_file():
            try:
                content = pkg_file.read_text(encoding="utf-8", errors="ignore")
                pkg_data = json.loads(content)

                # Always identify Node.js and JavaScript if package.json exists
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="JavaScript",
                        canonical_skill=skill_normalizer.normalize("JavaScript"),
                        evidence_type=EvidenceType.DEPENDENCY.value,
                        source_file="package.json",
                        description="JavaScript runtime package configuration.",
                        confidence=0.95,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )

                deps: Dict[str, str] = {}
                if isinstance(pkg_data.get("dependencies"), dict):
                    deps.update(pkg_data["dependencies"])
                if isinstance(pkg_data.get("devDependencies"), dict):
                    deps.update(pkg_data["devDependencies"])

                for pkg_name, version in deps.items():
                    norm_name = pkg_name.lower().strip()
                    if norm_name in PACKAGE_MAPPING:
                        tech_name, tech_cat = PACKAGE_MAPPING[norm_name]
                        canonical = skill_normalizer.normalize(tech_name)
                        items.append(
                            EvidenceItem(
                                project_id=project_id,
                                technology=tech_name,
                                canonical_skill=canonical,
                                evidence_type=EvidenceType.DEPENDENCY.value,
                                source_file="package.json",
                                source_location=f"dependencies.{pkg_name}",
                                description=f"Direct package dependency '{pkg_name}' version '{version}'.",
                                confidence=0.98,
                                confidence_level=ConfidenceLevel.VERIFIED.value,
                                detector=self.name,
                                snippet=f'"{pkg_name}": "{version}"',
                            )
                        )

            except Exception as exc:
                logger.warning(f"Error parsing package.json in '{repo_path}': {exc}")

        # 2. Inspect tsconfig.json (TypeScript configuration)
        tsconfig_file = repo_path / "tsconfig.json"
        if tsconfig_file.is_file():
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="TypeScript",
                    canonical_skill=skill_normalizer.normalize("TypeScript"),
                    evidence_type=EvidenceType.CONFIGURATION.value,
                    source_file="tsconfig.json",
                    description="TypeScript project compiler configuration file present.",
                    confidence=0.99,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

        return items
