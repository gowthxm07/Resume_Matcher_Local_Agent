"""
Base detector interface for CareerCrew repository technology analysis.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel


class BaseDetector(ABC):
    """
    Abstract technology detector interface.
    Each detector inspects repository files deterministically and emits EvidenceItem objects.
    """

    name: str = "base_detector"

    @abstractmethod
    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        """
        Inspect the local repository directory and return detected evidence items.
        Must be read-only and never execute code or shell commands.
        """
        pass
