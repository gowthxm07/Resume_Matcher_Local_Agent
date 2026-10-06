"""
Deterministic demonstration datasets for CareerCrew Phase 7 validation.
Safe to commit with zero personal or proprietary information.
"""

import json
from pathlib import Path
from typing import Dict, Any

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "fixtures"


def load_dataset_a() -> Dict[str, Any]:
    """Load Dataset A: Strong match candidate with corroborating local repository evidence."""
    path = FIXTURES_DIR / "dataset_a_strong_match.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_dataset_b() -> Dict[str, Any]:
    """Load Dataset B: Candidate with severe skill gaps and ungrounded metric claims."""
    path = FIXTURES_DIR / "dataset_b_evidence_gaps.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


DATASET_A = load_dataset_a()
DATASET_B = load_dataset_b()
