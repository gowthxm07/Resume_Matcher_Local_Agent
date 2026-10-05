"""
Documentation technology detector.
Inspects README and markdown files for claimed technologies.
CRITICAL RULE: Confidence is capped strictly at 0.50 (WEAK) and can NEVER yield a VERIFIED status on its own.
"""

import re
from pathlib import Path
from typing import List, Set
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer


class DocumentationDetector(BaseDetector):
    """
    Inspects README files for mentioned technologies.
    Emits low-confidence (WEAK) evidence records that cannot verify a claim alone.
    """

    name = "documentation_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        found_skills: Set[str] = set()

        readme_candidates = [
            repo_path / "README.md",
            repo_path / "readme.md",
            repo_path / "README.rst",
            repo_path / "README.txt",
        ]

        for r_file in readme_candidates:
            if not r_file.is_file():
                continue

            rel_file = str(r_file.relative_to(repo_path))
            try:
                content = r_file.read_text(encoding="utf-8", errors="ignore")[:10000]
                known_skills = skill_normalizer.find_all_known_skills(content)

                for skill in known_skills:
                    if skill in found_skills:
                        continue

                    # Make sure it appears as a distinct word in the README
                    pattern = rf"\b{re.escape(skill)}\b"
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        found_skills.add(skill)
                        canonical = skill_normalizer.normalize(skill)
                        items.append(
                            EvidenceItem(
                                project_id=project_id,
                                technology=skill,
                                canonical_skill=canonical,
                                evidence_type=EvidenceType.DOCUMENTATION.value,
                                source_file=rel_file,
                                description=f"Technology mentioned in documentation/README. (Indirect supporting signal only).",
                                confidence=0.45,  # Capped at WEAK confidence
                                confidence_level=ConfidenceLevel.WEAK.value,
                                detector=self.name,
                                snippet=match.group(0).strip(),
                            )
                        )

            except Exception:
                pass
            break

        return items
