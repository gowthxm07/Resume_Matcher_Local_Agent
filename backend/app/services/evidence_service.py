"""
Core Evidence Service for CareerCrew.
Coordinates project registration, Git metadata extraction, deterministic technology detection,
evidence caching, resume claim verification, and evidence chain assessment.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func

from app.core.logging import logger
from app.models.project import Project
from app.models.evidence_record import EvidenceRecord
from app.services.path_validator import path_validator, SecurityValidationError
from app.services.git_scanner import git_scanner
from app.services.detectors import detector_registry
from app.services.skill_normalizer import skill_normalizer
from app.schemas.evidence import (
    ConfidenceLevel,
    EvidenceItem,
    ProjectResponse,
    SkillVerificationResult,
    EvidenceChainItem,
    EvidenceAssessment,
    GitMetadata,
)
from app.schemas.intelligence import ResumeProfile, JobProfile, AnalysisResult


class EvidenceService:
    """
    Manages local repository registration, evidence collection, and resume claim grounding.
    Enforces strict read-only guarantees with zero paid cloud APIs.
    """

    # Confidence thresholds
    VERIFIED_THRESHOLD = 0.85
    LIKELY_THRESHOLD = 0.65
    WEAK_THRESHOLD = 0.40

    @classmethod
    def register_project(
        cls,
        *args,
        db: Optional[Session] = None,
        name: Optional[str] = None,
        path_str: Optional[str] = None,
        repo_path: Optional[str] = None,
        path: Optional[str] = None,
        description: str = "",
        **kwargs,
    ) -> ProjectResponse:
        """
        Validate path security, inspect Git metadata, and register project in SQLite.
        Accepts flexible positional or keyword arguments.
        """
        resolved_db: Optional[Session] = db
        resolved_name: Optional[str] = name
        resolved_path: Optional[str] = repo_path or path_str or path
        resolved_desc: str = description

        # Resolve positional arguments if passed
        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, str):
                if resolved_name is None:
                    resolved_name = arg
                elif resolved_path is None:
                    resolved_path = arg
                elif not resolved_desc:
                    resolved_desc = arg

        if not resolved_db:
            raise ValueError("Database session is required to register a project.")
        if not resolved_name or not resolved_path:
            raise ValueError("Project name and path are required.")

        # 1. Security & path validation
        validated_path = path_validator.validate_project_path(resolved_path)
        canonical_path_str = str(validated_path)

        # 2. Check if project with this path already registered
        existing = resolved_db.scalar(select(Project).where(Project.repo_path == canonical_path_str))
        if existing:
            logger.info(f"Project path '{canonical_path_str}' already registered (id={existing.id})")
            return cls._to_project_response(existing, resolved_db)

        # 3. Extract Git metadata
        git_meta: GitMetadata = git_scanner.scan_repository(validated_path)

        # 4. Create and persist Project entity
        project = Project(
            name=resolved_name.strip(),
            description=resolved_desc.strip(),
            repo_path=canonical_path_str,
            status="pending",
            git_remote=git_meta.remote_url,
            git_branch=git_meta.branch,
            head_commit=git_meta.head_commit,
            commit_count=git_meta.commit_count,
            evidence_metadata={
                "is_git_repo": git_meta.is_git_repo,
                "first_commit_date": git_meta.first_commit_date,
                "last_commit_date": git_meta.last_commit_date,
                "author_stats": git_meta.author_stats,
            },
        )
        resolved_db.add(project)
        resolved_db.commit()
        resolved_db.refresh(project)

        # 5. Automatically perform initial evidence scan
        cls.scan_project(resolved_db, project.id, force_refresh=True)
        resolved_db.refresh(project)

        return cls._to_project_response(project, resolved_db)

    @classmethod
    def scan_project(
        cls,
        *args,
        db: Optional[Session] = None,
        project_id: Optional[str] = None,
        project: Optional[Any] = None,
        force_refresh: bool = False,
        force: bool = False,
        **kwargs,
    ) -> ProjectResponse:
        """
        Execute deterministic technology detection across the registered project directory.
        Reuses previous scan results if Git HEAD commit has not changed and force_refresh is False.
        """
        resolved_db: Optional[Session] = db
        resolved_id: Optional[str] = project_id
        resolved_proj: Optional[Project] = project
        resolved_force: bool = force_refresh or force

        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, Project):
                resolved_proj = arg
                resolved_id = arg.id
            elif isinstance(arg, str):
                resolved_id = arg
            elif isinstance(arg, bool):
                resolved_force = arg

        if not resolved_db:
            raise ValueError("Database session is required to scan project.")

        if not resolved_proj:
            if not resolved_id:
                raise ValueError("Project ID or Project instance is required.")
            resolved_proj = resolved_db.scalar(select(Project).where(Project.id == resolved_id))

        if not resolved_proj:
            raise ValueError(f"Project '{resolved_id}' not found")

        repo_path = Path(resolved_proj.repo_path)
        if not repo_path.exists():
            resolved_proj.status = "error"
            resolved_db.commit()
            raise ValueError(f"Registered project directory no longer exists: {repo_path}")

        # 1. Inspect current git state
        git_meta = git_scanner.scan_repository(repo_path)

        # 2. Performance check: If HEAD commit hasn't changed and records exist, reuse
        if (
            not resolved_force
            and resolved_proj.head_commit
            and resolved_proj.head_commit == git_meta.head_commit
            and resolved_proj.last_scanned_at
        ):
            ev_count = resolved_db.scalar(
                select(func.count(EvidenceRecord.id)).where(EvidenceRecord.project_id == resolved_proj.id)
            ) or 0
            if ev_count > 0:
                logger.info(f"Skipping re-scan for '{resolved_proj.name}': HEAD commit unchanged ({resolved_proj.head_commit[:8]}).")
                return cls._to_project_response(resolved_proj, resolved_db)

        logger.info(f"Scanning project directory '{repo_path}' for technical evidence...")

        # 3. Clear existing evidence records for clean update
        resolved_db.execute(delete(EvidenceRecord).where(EvidenceRecord.project_id == resolved_proj.id))
        resolved_db.commit()

        # 4. Run all registered technology detectors
        evidence_items = detector_registry.run_all_detectors(repo_path, resolved_proj.id)

        # 5. Persist evidence items to SQLite
        detected_techs_set = set()
        for item in evidence_items:
            detected_techs_set.add(item.technology)
            rec = EvidenceRecord(
                project_id=resolved_proj.id,
                technology=item.technology,
                canonical_skill=item.canonical_skill,
                evidence_type=item.evidence_type,
                source_file=item.source_file,
                source_location=item.source_location,
                description=item.description,
                confidence=item.confidence,
                confidence_level=item.confidence_level,
                detector=item.detector,
                snippet=item.snippet,
            )
            resolved_db.add(rec)

        # 6. Update Project status and metadata
        resolved_proj.status = "verified"
        resolved_proj.head_commit = git_meta.head_commit
        resolved_proj.commit_count = git_meta.commit_count
        resolved_proj.git_branch = git_meta.branch
        resolved_proj.last_scanned_at = datetime.now(timezone.utc)
        meta = dict(resolved_proj.evidence_metadata or {})
        meta["detected_technologies"] = sorted(list(detected_techs_set))
        meta["evidence_count"] = len(evidence_items)
        resolved_proj.evidence_metadata = meta

        resolved_db.commit()
        resolved_db.refresh(resolved_proj)

        logger.info(f"Scan complete for '{resolved_proj.name}': {len(evidence_items)} evidence records found.")
        return cls._to_project_response(resolved_proj, resolved_db)

    @classmethod
    def list_projects(cls, db: Session) -> List[ProjectResponse]:
        """List all registered projects."""
        projects = db.scalars(select(Project).order_by(Project.created_at.desc())).all()
        return [cls._to_project_response(p, db) for p in projects]

    @classmethod
    def get_project_summary(
        cls,
        *args,
        db: Optional[Session] = None,
        project_id: Optional[str] = None,
        **kwargs,
    ) -> Optional[ProjectResponse]:
        """Retrieve project summary response by ID."""
        resolved_db = db
        resolved_id = project_id
        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, str):
                resolved_id = arg

        if not resolved_db or not resolved_id:
            return None

        project = resolved_db.scalar(select(Project).where(Project.id == resolved_id))
        if not project:
            return None
        return cls._to_project_response(project, resolved_db)

    @classmethod
    def get_project_evidence(
        cls,
        *args,
        db: Optional[Session] = None,
        project_id: Optional[str] = None,
        technology: Optional[str] = None,
        **kwargs,
    ) -> List[EvidenceItem]:
        """Retrieve atomic evidence records for a project."""
        resolved_db = db
        resolved_id = project_id
        resolved_tech = technology

        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, str):
                if resolved_id is None:
                    resolved_id = arg
                elif resolved_tech is None:
                    resolved_tech = arg

        if not resolved_db or not resolved_id:
            return []

        stmt = select(EvidenceRecord).where(EvidenceRecord.project_id == resolved_id)
        if resolved_tech:
            canonical = skill_normalizer.normalize(resolved_tech)
            stmt = stmt.where(EvidenceRecord.canonical_skill == canonical)

        records = resolved_db.scalars(stmt.order_by(EvidenceRecord.confidence.desc())).all()
        return [cls._to_evidence_item(r) for r in records]

    @classmethod
    def verify_skill(
        cls,
        *args,
        db: Optional[Session] = None,
        raw_skill: Optional[str] = None,
        skill: Optional[str] = None,
        **kwargs,
    ) -> SkillVerificationResult:
        """
        Verify a single technical skill against all registered local projects.
        Applies canonical normalization and the documented confidence hierarchy.
        Accepts (skill, db) or (db, skill).
        """
        resolved_db = db
        resolved_skill = raw_skill or skill

        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, str):
                resolved_skill = arg

        if not resolved_db or not resolved_skill:
            raise ValueError("Both skill name and database session are required to verify skill.")

        canonical = skill_normalizer.normalize(resolved_skill)

        # Query all evidence records across all registered projects
        records = resolved_db.scalars(
            select(EvidenceRecord).where(EvidenceRecord.canonical_skill == canonical)
        ).all()

        if not records:
            return SkillVerificationResult(
                skill=resolved_skill,
                canonical_skill=canonical,
                status=ConfidenceLevel.UNVERIFIED.value,
                confidence=0.0,
                projects=[],
                evidence_count=0,
                evidence_records=[],
                summary=f"No local repository evidence found for '{canonical}'.",
            )

        # Group by project and find max confidence
        project_ids = list(set(r.project_id for r in records))
        projects = resolved_db.scalars(select(Project).where(Project.id.in_(project_ids))).all()
        project_names = [p.name for p in projects]

        # Highest confidence record determines primary status
        max_conf = max(r.confidence for r in records)
        direct_impl_count = sum(
            1 for r in records if r.evidence_type in ["dependency", "configuration", "source_code", "database_schema", "infrastructure"]
        )

        # Confidence Hierarchy Determination
        if max_conf >= cls.VERIFIED_THRESHOLD and direct_impl_count >= 1:
            status = ConfidenceLevel.VERIFIED.value
            summary = f"Verified with {direct_impl_count} direct implementation/config evidence record(s) across {len(project_names)} project(s)."
        elif max_conf >= cls.LIKELY_THRESHOLD:
            status = ConfidenceLevel.LIKELY.value
            summary = f"Likely supported by {len(records)} supporting signal(s) across {len(project_names)} project(s)."
        elif max_conf >= cls.WEAK_THRESHOLD:
            status = ConfidenceLevel.WEAK.value
            summary = f"Weak evidence: mentioned only in documentation without direct implementation proof."
        else:
            status = ConfidenceLevel.UNVERIFIED.value
            summary = f"Insufficient evidence (< {cls.WEAK_THRESHOLD*100}% confidence)."

        return SkillVerificationResult(
            skill=resolved_skill,
            canonical_skill=canonical,
            status=status,
            confidence=round(max_conf, 2),
            projects=project_names,
            evidence_count=len(records),
            evidence_records=[cls._to_evidence_item(r) for r in records],
            summary=summary,
        )

    @classmethod
    def verify_resume_skills(
        cls,
        *args,
        db: Optional[Session] = None,
        resume: Optional[ResumeProfile] = None,
        **kwargs,
    ) -> List[SkillVerificationResult]:
        """Verify all technical skills extracted from a ResumeProfile against registered projects."""
        resolved_db = db
        resolved_resume = resume

        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, ResumeProfile):
                resolved_resume = arg

        if not resolved_db or not resolved_resume:
            return []

        all_skills = []
        if resolved_resume.skills:
            all_skills.extend(resolved_resume.skills.programming_languages)
            all_skills.extend(resolved_resume.skills.frameworks)
            all_skills.extend(resolved_resume.skills.databases)
            all_skills.extend(resolved_resume.skills.cloud_platforms)
            all_skills.extend(resolved_resume.skills.tools_and_devops)

        unique_canonicals = {}
        for s in all_skills:
            can = skill_normalizer.normalize(s)
            if can not in unique_canonicals:
                unique_canonicals[can] = s

        results: List[SkillVerificationResult] = []
        for can, raw in unique_canonicals.items():
            results.append(cls.verify_skill(resolved_db, raw))

        return sorted(results, key=lambda x: (x.status != "VERIFIED", x.status != "LIKELY", -x.confidence))

    @classmethod
    def build_evidence_chain(
        cls,
        *args,
        db: Optional[Session] = None,
        job: Optional[JobProfile] = None,
        resume: Optional[ResumeProfile] = None,
        **kwargs,
    ) -> EvidenceAssessment:
        """
        Build the unified chain:
        Job Requirement -> Resume Claim -> Project -> Repository Evidence
        Calculates an independent Evidence Confidence Score.
        """
        resolved_db = db
        resolved_job = job
        resolved_resume = resume

        for arg in args:
            if isinstance(arg, Session):
                resolved_db = arg
            elif isinstance(arg, JobProfile):
                resolved_job = arg
            elif isinstance(arg, ResumeProfile):
                resolved_resume = arg

        if not resolved_db:
            raise ValueError("Database session is required to build evidence chain.")

        projects_count = resolved_db.scalar(select(func.count(Project.id))) or 0

        # Extract all claimed resume skills
        claimed_skills_canonical = set()
        if resolved_resume and resolved_resume.skills:
            for s in (
                resolved_resume.skills.programming_languages
                + resolved_resume.skills.frameworks
                + resolved_resume.skills.databases
                + resolved_resume.skills.cloud_platforms
                + resolved_resume.skills.tools_and_devops
            ):
                claimed_skills_canonical.add(skill_normalizer.normalize(s).lower())

        chain_items: List[EvidenceChainItem] = []
        verified_count = 0
        likely_count = 0
        weak_count = 0
        unverified_count = 0

        # Iterate all categorized job requirements
        requirements = []
        if resolved_job:
            requirements = list(resolved_job.categorized_requirements or [])
            if not requirements and (resolved_job.required_skills or resolved_job.preferred_skills):
                from app.services.requirement_classifier import RequirementClassifier
                requirements = RequirementClassifier.classify_requirements_list(
                    required_skills=resolved_job.required_skills,
                    preferred_skills=resolved_job.preferred_skills,
                )

        for req in requirements:
            can_skill = req.canonical_skill
            is_claimed = can_skill.lower() in claimed_skills_canonical

            # Query project evidence
            verif_res = cls.verify_skill(resolved_db, can_skill)

            if verif_res.status == ConfidenceLevel.VERIFIED.value:
                verified_count += 1
            elif verif_res.status == ConfidenceLevel.LIKELY.value:
                likely_count += 1
            elif verif_res.status == ConfidenceLevel.WEAK.value:
                weak_count += 1
            else:
                unverified_count += 1

            # Format human rationale
            if verif_res.status == ConfidenceLevel.VERIFIED.value:
                rationale = f"Verified with {verif_res.evidence_count} evidence record(s) in {', '.join(verif_res.projects)}."
            elif verif_res.status == ConfidenceLevel.LIKELY.value:
                rationale = f"Likely supported by signals in {', '.join(verif_res.projects)}."
            elif verif_res.status == ConfidenceLevel.WEAK.value:
                rationale = f"Weak documentation evidence only."
            else:
                if is_claimed:
                    rationale = "Claimed on resume, but no local project evidence found in registered repositories."
                else:
                    rationale = "Not claimed on resume and no local repository evidence found."

            chain_items.append(
                EvidenceChainItem(
                    requirement=req.original_text,
                    canonical_skill=can_skill,
                    requirement_type=req.requirement_type.value if hasattr(req.requirement_type, "value") else str(req.requirement_type),
                    resume_claimed=is_claimed,
                    resume_evidence="Listed in candidate skills inventory" if is_claimed else None,
                    projects_found=verif_res.projects,
                    verification_status=verif_res.status,
                    verification_confidence=verif_res.confidence,
                    repository_evidence=verif_res.evidence_records,
                    rationale=rationale,
                )
            )

        # Calculate independent Evidence Confidence Score
        total_reqs = len(requirements)
        if total_reqs > 0:
            evidence_points = (
                (verified_count * 1.0)
                + (likely_count * 0.7)
                + (weak_count * 0.3)
                + (unverified_count * 0.0)
            )
            evidence_confidence_score = round(min(100.0, (evidence_points / total_reqs) * 100.0), 1)
            coverage_pct = round(((verified_count + likely_count) / total_reqs) * 100.0, 1)
        else:
            evidence_confidence_score = 0.0
            coverage_pct = 0.0

        return EvidenceAssessment(
            evidence_confidence_score=evidence_confidence_score,
            verified_skills_count=verified_count,
            likely_skills_count=likely_count,
            weak_skills_count=weak_count,
            unverified_skills_count=unverified_count,
            evidence_coverage_percentage=coverage_pct,
            chain=chain_items,
            scanned_projects_count=projects_count,
        )

    # ---------------------------------------------------------
    # MAPPERS
    # ---------------------------------------------------------

    @staticmethod
    def _to_project_response(project: Project, db: Session) -> ProjectResponse:
        ev_count = db.scalar(
            select(func.count(EvidenceRecord.id)).where(EvidenceRecord.project_id == project.id)
        ) or 0
        detected_techs = (project.evidence_metadata or {}).get("detected_technologies", [])

        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description or "",
            repo_path=project.repo_path,
            status=project.status,
            git_remote=project.git_remote,
            git_branch=project.git_branch,
            head_commit=project.head_commit,
            commit_count=project.commit_count or 0,
            last_scanned_at=project.last_scanned_at.isoformat() if project.last_scanned_at else None,
            evidence_count=ev_count,
            detected_technologies=detected_techs,
            created_at=project.created_at.isoformat() if project.created_at else "",
        )

    @staticmethod
    def _to_evidence_item(r: EvidenceRecord) -> EvidenceItem:
        return EvidenceItem(
            id=r.id,
            project_id=r.project_id,
            technology=r.technology,
            canonical_skill=r.canonical_skill,
            evidence_type=r.evidence_type,
            source_file=r.source_file,
            source_location=r.source_location,
            description=r.description,
            confidence=r.confidence,
            confidence_level=r.confidence_level,
            detector=r.detector,
            snippet=r.snippet,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )


evidence_service = EvidenceService()
