"""
Extensible technology detector registry.
Coordinates all specialized ecosystem detectors to collect repository evidence.
"""

from pathlib import Path
from typing import List, Dict
from app.services.detectors.base import BaseDetector
from app.services.detectors.package_json_detector import PackageJsonDetector
from app.services.detectors.python_detector import PythonDetector
from app.services.detectors.container_infra_detector import ContainerInfraDetector
from app.services.detectors.database_detector import DatabaseDetector
from app.services.detectors.frontend_detector import FrontendDetector
from app.services.detectors.java_detector import JavaDetector
from app.services.detectors.source_code_detector import SourceCodeDetector
from app.services.detectors.documentation_detector import DocumentationDetector
from app.schemas.evidence import EvidenceItem, ConfidenceLevel
from app.core.logging import logger


class DetectorRegistry:
    """
    Registry managing all repository technology detectors.
    Runs detectors sequentially in deterministic order.
    """

    def __init__(self):
        self._detectors: List[BaseDetector] = [
            PackageJsonDetector(),
            PythonDetector(),
            ContainerInfraDetector(),
            DatabaseDetector(),
            FrontendDetector(),
            JavaDetector(),
            SourceCodeDetector(),
            DocumentationDetector(),
        ]

    def register_detector(self, detector: BaseDetector):
        """Allow extending the registry with additional custom detectors."""
        self._detectors.append(detector)

    def scan_repository(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        """
        Run all registered detectors against the repository path.
        Returns aggregated evidence items.
        """
        all_items: List[EvidenceItem] = []

        for detector in self._detectors:
            try:
                items = detector.detect(repo_path, project_id)
                all_items.extend(items)
            except Exception as exc:
                logger.warning(f"Error running detector '{detector.name}' on '{repo_path}': {exc}")

        # Deduplicate and sort items
        return self._deduplicate_evidence(all_items)

    def run_all_detectors(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        """Alias for scan_repository."""
        return self.scan_repository(repo_path, project_id)


    @staticmethod
    def _deduplicate_evidence(items: List[EvidenceItem]) -> List[EvidenceItem]:
        """
        Deduplicate evidence items matching the same canonical skill, source file, and evidence type.
        Preserves highest confidence item.
        """
        seen: Dict[str, EvidenceItem] = {}

        for item in items:
            key = f"{item.canonical_skill.lower()}:{item.source_file}:{item.evidence_type}"
            if key not in seen:
                seen[key] = item
            else:
                if item.confidence > seen[key].confidence:
                    seen[key] = item

        # Sort by confidence descending
        return sorted(seen.values(), key=lambda x: x.confidence, reverse=True)


detector_registry = DetectorRegistry()

__all__ = [
    "BaseDetector",
    "PackageJsonDetector",
    "PythonDetector",
    "ContainerInfraDetector",
    "DatabaseDetector",
    "FrontendDetector",
    "JavaDetector",
    "SourceCodeDetector",
    "DocumentationDetector",
    "DetectorRegistry",
    "detector_registry",
]
