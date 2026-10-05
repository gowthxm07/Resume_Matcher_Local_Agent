"""
Container, infrastructure, and cloud configuration technology detector.
Inspects Dockerfiles, Docker Compose services, Kubernetes manifests, Helm, and Terraform.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from app.services.detectors.base import BaseDetector
from app.schemas.evidence import EvidenceItem, EvidenceType, ConfidenceLevel
from app.services.skill_normalizer import skill_normalizer
from app.core.logging import logger

COMPOSE_SERVICE_IMAGES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "redis": "Redis",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "mariadb": "MySQL",
    "rabbitmq": "RabbitMQ",
    "elasticsearch": "Elasticsearch",
    "nginx": "Nginx",
}


class ContainerInfraDetector(BaseDetector):
    """Detects Docker, Compose, Kubernetes, and containerized services."""

    name = "container_infra_detector"

    def detect(self, repo_path: Path, project_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # 1. Dockerfile detection
        dockerfile = repo_path / "Dockerfile"
        if dockerfile.is_file():
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Docker",
                    canonical_skill=skill_normalizer.normalize("Docker"),
                    evidence_type=EvidenceType.INFRASTRUCTURE.value,
                    source_file="Dockerfile",
                    description="Dockerfile container build recipe defined.",
                    confidence=0.99,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

        # 2. Docker Compose detection
        compose_candidates = [
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        ]

        for c_name in compose_candidates:
            c_file = repo_path / c_name
            if c_file.is_file():
                items.append(

                    EvidenceItem(
                        project_id=project_id,
                        technology="Docker",
                        canonical_skill=skill_normalizer.normalize("Docker"),
                        evidence_type=EvidenceType.INFRASTRUCTURE.value,
                        source_file=c_name,
                        description="Docker Compose multi-container orchestration manifest present.",
                        confidence=0.99,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )
                items.append(
                    EvidenceItem(
                        project_id=project_id,
                        technology="Docker Compose",
                        canonical_skill="docker",
                        evidence_type=EvidenceType.INFRASTRUCTURE.value,
                        source_file=c_name,
                        description="Docker Compose configuration.",
                        confidence=0.99,
                        confidence_level=ConfidenceLevel.VERIFIED.value,
                        detector=self.name,
                    )
                )


                try:
                    content = c_file.read_text(encoding="utf-8", errors="ignore")
                    # Inspect configured services/images in Docker Compose
                    for image_key, tech in COMPOSE_SERVICE_IMAGES.items():
                        # Look for image: postgres:16 or image: redis:alpine
                        pattern = rf"""image:\s*['"]?({image_key}(?::[a-zA-Z0-9_\-\.]+)?)['"]?"""
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            canonical = skill_normalizer.normalize(tech)
                            items.append(
                                EvidenceItem(
                                    project_id=project_id,
                                    technology=tech,
                                    canonical_skill=canonical,
                                    evidence_type=EvidenceType.CONFIGURATION.value,
                                    source_file=c_name,
                                    description=f"{tech} service configured in Docker Compose ({match.group(0).strip()}).",
                                    confidence=0.98,
                                    confidence_level=ConfidenceLevel.VERIFIED.value,
                                    detector=self.name,
                                    snippet=match.group(0).strip(),
                                )
                            )
                except Exception as exc:
                    logger.warning(f"Error parsing {c_name} in '{repo_path}': {exc}")
                break

        # 3. Kubernetes manifests
        k8s_dirs = [repo_path / "k8s", repo_path / "kubernetes", repo_path / "deploy"]
        found_k8s = False
        for kdir in k8s_dirs:
            if kdir.is_dir():
                for yml in kdir.glob("*.y*ml"):
                    try:
                        content = yml.read_text(encoding="utf-8", errors="ignore")[:1000]
                        if "apiVersion:" in content and ("kind: Deployment" in content or "kind: Service" in content):
                            found_k8s = True
                            items.append(
                                EvidenceItem(
                                    project_id=project_id,
                                    technology="Kubernetes",
                                    canonical_skill=skill_normalizer.normalize("Kubernetes"),
                                    evidence_type=EvidenceType.INFRASTRUCTURE.value,
                                    source_file=str(yml.relative_to(repo_path)),
                                    description="Kubernetes workload manifest defined.",
                                    confidence=0.98,
                                    confidence_level=ConfidenceLevel.VERIFIED.value,
                                    detector=self.name,
                                )
                            )
                            break
                    except Exception:
                        pass
                if found_k8s:
                    break

        # 4. Terraform
        tf_files = list(repo_path.glob("*.tf"))
        if tf_files:
            items.append(
                EvidenceItem(
                    project_id=project_id,
                    technology="Terraform",
                    canonical_skill=skill_normalizer.normalize("Terraform"),
                    evidence_type=EvidenceType.INFRASTRUCTURE.value,
                    source_file=str(tf_files[0].relative_to(repo_path)),
                    description="Terraform infrastructure-as-code configuration present.",
                    confidence=0.98,
                    confidence_level=ConfidenceLevel.VERIFIED.value,
                    detector=self.name,
                )
            )

        return items
