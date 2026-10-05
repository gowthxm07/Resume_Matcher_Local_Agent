"""
Structured document extraction service powered by local Ollama (Llama 3.2:3b).
Extracts strictly grounded ResumeProfile and JobProfile instances with resilient JSON parsing,
SHA-256 caching, and deterministic fallback heuristics when LLM is unavailable.
"""

import hashlib
import json
import re
from typing import Dict, Any, Optional, List
from app.core.logging import logger
from app.services.ollama_service import ollama_service
from app.services.skill_normalizer import skill_normalizer
from app.services.requirement_classifier import RequirementClassifier
from app.schemas.intelligence import (
    ResumeProfile,
    ContactMetadata,
    SkillsInventory,
    WorkExperienceItem,
    EducationItem,
    ProjectItem,
    JobProfile,
    CategorizedRequirement,
    RequirementType,
    SkillCategory,
)


def compute_sha256(text: str) -> str:
    """Compute deterministic SHA-256 hash of raw input text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_json_from_llm_response(text: str) -> Optional[Dict[str, Any]]:
    """
    Resilient JSON extractor that parses JSON objects from LLM outputs,
    stripping markdown fences (```json ... ```) and repairing common formatting issues.
    """
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # 1. Look for ```json ... ``` code fence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Look for outermost curly braces
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Try removing trailing commas
            candidate_repaired = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(candidate_repaired)
            except json.JSONDecodeError:
                pass

    # 3. Direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


class ExtractorService:
    """
    Extracts structured profiles from candidate resumes and job descriptions
    using local Ollama with deterministic rule-based fallbacks and hash caching.
    """

    def __init__(self):
        # In-memory profile caches keyed by raw_text_hash
        self._resume_cache: Dict[str, ResumeProfile] = {}
        self._jd_cache: Dict[str, JobProfile] = {}

    # ---------------------------------------------------------
    # RESUME EXTRACTION
    # ---------------------------------------------------------

    async def extract_resume(
        self,
        raw_text: str,
        force_refresh: bool = False,
    ) -> ResumeProfile:
        """
        Extract structured ResumeProfile from raw resume text.
        """
        text_hash = compute_sha256(raw_text)
        if not force_refresh and text_hash in self._resume_cache:
            logger.info(f"Resume profile cache hit (hash={text_hash[:8]})")
            return self._resume_cache[text_hash]

        logger.info(f"Extracting structured ResumeProfile (text_len={len(raw_text)})")

        profile = None
        ollama_avail = await ollama_service.check_availability()

        if ollama_avail["reachable"]:
            profile = await self._extract_resume_llm(raw_text, text_hash)

        # Fallback if LLM failed, unreachable, or produced malformed JSON
        if profile is None:
            logger.info("Using deterministic fallback extraction for resume")
            profile = self._extract_resume_deterministic(raw_text, text_hash)

        self._resume_cache[text_hash] = profile
        return profile

    async def _extract_resume_llm(
        self,
        raw_text: str,
        text_hash: str,
    ) -> Optional[ResumeProfile]:
        """Query local Ollama to deconstruct the resume into JSON."""
        system_prompt = (
            "You are a strict resume parsing engine. Transform the candidate resume into valid JSON.\n"
            "RULES:\n"
            "1. DO NOT invent or fabricate any skills, employers, dates, or metrics.\n"
            "2. If a section is missing from the resume, return an empty array or null.\n"
            "3. Extract exact technical skills into programming_languages, frameworks, databases, cloud_platforms, tools.\n"
            "4. Return ONLY a single valid JSON object. No conversational preamble or postscript."
        )

        user_prompt = f"""Extract the structured profile from this resume:
---
{raw_text[:6000]}
---

JSON Schema:
{{
  "candidate_name": "Full Name or null",
  "contact_info": {{
    "email": "email or null",
    "phone": "phone or null",
    "location": "location or null",
    "linkedin_url": "url or null",
    "github_url": "url or null"
  }},
  "summary": "Professional summary or null",
  "skills": {{
    "programming_languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "libraries": ["PyMuPDF", "Pydantic"],
    "databases": ["PostgreSQL", "SQLite"],
    "cloud_platforms": ["AWS", "Docker"],
    "tools_and_devops": ["Git", "Linux"],
    "soft_skills": ["Leadership"]
  }},
  "work_experience": [
    {{
      "organization": "Company",
      "role": "Role",
      "duration": "2022 - Present",
      "responsibilities": ["Developed local APIs"],
      "technologies": ["Python", "FastAPI"],
      "measurable_achievements": ["Reduced latency by 40%"]
    }}
  ],
  "education": [
    {{
      "institution": "University",
      "degree": "B.S. in Computer Science",
      "field_of_study": "Computer Science",
      "graduation_year": "2024"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Project summary",
      "technologies": ["Python", "Ollama"],
      "measurable_results": ["Processed 1000 docs/sec"]
    }}
  ],
  "certifications": ["AWS Certified Developer"]
}}"""

        res = await ollama_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2048,
        )

        if not res["success"]:
            logger.warning(f"Ollama generation failed for resume: {res.get('error')}")
            return None

        parsed_json = extract_json_from_llm_response(res["response_text"])
        if not parsed_json:
            logger.warning("Failed to parse valid JSON from Ollama resume response")
            return None

        try:
            # Build ResumeProfile from validated JSON
            contact = parsed_json.get("contact_info") or {}
            skills_dict = parsed_json.get("skills") or {}

            # Normalize extracted skills deterministically
            prog_langs = [skill_normalizer.normalize(s) for s in (skills_dict.get("programming_languages") or []) if s]
            frameworks = [skill_normalizer.normalize(s) for s in (skills_dict.get("frameworks") or []) if s]
            databases = [skill_normalizer.normalize(s) for s in (skills_dict.get("databases") or []) if s]
            cloud = [skill_normalizer.normalize(s) for s in (skills_dict.get("cloud_platforms") or []) if s]
            tools = [skill_normalizer.normalize(s) for s in (skills_dict.get("tools_and_devops") or []) if s]

            skills_inv = SkillsInventory(
                programming_languages=prog_langs,
                frameworks=frameworks,
                libraries=skills_dict.get("libraries") or [],
                databases=databases,
                cloud_platforms=cloud,
                tools_and_devops=tools,
                soft_skills=skills_dict.get("soft_skills") or [],
                other=skills_dict.get("other") or [],
            )

            work_items = []
            for w in (parsed_json.get("work_experience") or []):
                if not isinstance(w, dict):
                    continue
                work_items.append(
                    WorkExperienceItem(
                        organization=w.get("organization") or "Organization",
                        role=w.get("role") or "Role",
                        duration=w.get("duration"),
                        responsibilities=w.get("responsibilities") or [],
                        technologies=[skill_normalizer.normalize(t) for t in (w.get("technologies") or []) if t],
                        measurable_achievements=w.get("measurable_achievements") or [],
                    )
                )

            edu_items = []
            for e in (parsed_json.get("education") or []):
                if not isinstance(e, dict):
                    continue
                edu_items.append(
                    EducationItem(
                        institution=e.get("institution") or "Institution",
                        degree=e.get("degree") or "Degree",
                        field_of_study=e.get("field_of_study"),
                        graduation_year=e.get("graduation_year"),
                        gpa=e.get("gpa"),
                    )
                )

            project_items = []
            for p in (parsed_json.get("projects") or []):
                if not isinstance(p, dict):
                    continue
                project_items.append(
                    ProjectItem(
                        name=p.get("name") or "Project",
                        description=p.get("description") or "",
                        technologies=[skill_normalizer.normalize(t) for t in (p.get("technologies") or []) if t],
                        responsibilities=p.get("responsibilities") or [],
                        measurable_results=p.get("measurable_results") or [],
                        links=p.get("links") or [],
                    )
                )

            profile = ResumeProfile(
                candidate_name=parsed_json.get("candidate_name"),
                contact_info=ContactMetadata(
                    email=contact.get("email"),
                    phone=contact.get("phone"),
                    location=contact.get("location"),
                    linkedin_url=contact.get("linkedin_url"),
                    github_url=contact.get("github_url"),
                ),
                summary=parsed_json.get("summary"),
                skills=skills_inv,
                work_experience=work_items,
                education=edu_items,
                projects=project_items,
                certifications=parsed_json.get("certifications") or [],
                achievements=parsed_json.get("achievements") or [],
                raw_text_hash=text_hash,
                extraction_metadata={
                    "method": "llm",
                    "model": res["model"],
                    "latency_ms": res["latency_ms"],
                },
            )
            return profile
        except Exception as exc:
            logger.warning(f"Error converting parsed JSON to ResumeProfile: {exc}")
            return None

    def _extract_resume_deterministic(
        self,
        raw_text: str,
        text_hash: str,
    ) -> ResumeProfile:
        """
        Deterministic regex and catalog parser fallback.
        Ensures zero-dependency reliability when Ollama is unavailable.
        """
        # 1. Contact info via regex
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
        phone_match = re.search(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", raw_text)
        github_match = re.search(r"github\.com/[\w\.-]+", raw_text, re.IGNORECASE)
        linkedin_match = re.search(r"linkedin\.com/in/[\w\.-]+", raw_text, re.IGNORECASE)

        contact = ContactMetadata(
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0) if phone_match else None,
            github_url=f"https://{github_match.group(0)}" if github_match else None,
            linkedin_url=f"https://{linkedin_match.group(0)}" if linkedin_match else None,
        )

        # 2. Extract known skills deterministically
        known_skills = skill_normalizer.find_all_known_skills(raw_text)
        prog_langs = []
        frameworks = []
        databases = []
        cloud = []
        tools = []
        other_skills = []

        for s in known_skills:
            cat = skill_normalizer.get_category(s)
            if cat == SkillCategory.PROGRAMMING_LANGUAGE:
                prog_langs.append(s)
            elif cat == SkillCategory.FRAMEWORK:
                frameworks.append(s)
            elif cat == SkillCategory.DATABASE:
                databases.append(s)
            elif cat == SkillCategory.CLOUD or cat == SkillCategory.DEVOPS:
                cloud.append(s)
            elif cat == SkillCategory.TOOL:
                tools.append(s)
            else:
                other_skills.append(s)

        skills = SkillsInventory(
            programming_languages=prog_langs,
            frameworks=frameworks,
            databases=databases,
            cloud_platforms=cloud,
            tools_and_devops=tools,
            other=other_skills,
        )

        # 3. Candidate name heuristic (typically first non-empty line)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        candidate_name = lines[0] if lines and len(lines[0]) < 60 else None

        # 4. Education, experience, and project heuristics
        edu_items = []
        work_items = []
        project_items = []
        current_section = None

        for line in lines:
            lowered = line.lower()
            if any(term in lowered for term in ["education:", "education"]):
                current_section = "education"
                continue
            elif any(term in lowered for term in ["experience:", "work experience:", "work experience", "employment"]):
                current_section = "experience"
                continue
            elif any(term in lowered for term in ["projects:", "project:", "personal projects", "key projects"]):
                current_section = "projects"
                continue
            elif any(term in lowered for term in ["skills:", "technical skills:"]):
                current_section = "skills"
                continue

            if any(term in lowered for term in ["bachelor", "master", "b.s.", "m.s.", "ph.d.", "degree in"]):
                edu_items.append(EducationItem(institution="Extracted Institution", degree=line))
            elif current_section == "experience" and len(line) > 10:
                line_techs = skill_normalizer.find_all_known_skills(line)
                work_items.append(
                    WorkExperienceItem(
                        organization="Company",
                        role="Software Engineer",
                        responsibilities=[line],
                        technologies=line_techs,
                    )
                )
            elif current_section == "projects" and len(line) > 10:
                line_techs = skill_normalizer.find_all_known_skills(line)
                name = line.split(":")[0] if ":" in line else "Project"
                project_items.append(
                    ProjectItem(
                        name=name.strip()[:60],
                        description=line,
                        technologies=line_techs,
                    )
                )

        return ResumeProfile(
            candidate_name=candidate_name,
            contact_info=contact,
            skills=skills,
            education=edu_items,
            work_experience=work_items,
            projects=project_items,
            raw_text_hash=text_hash,
            extraction_metadata={"method": "deterministic_fallback"},
        )

    # ---------------------------------------------------------
    # JOB DESCRIPTION EXTRACTION
    # ---------------------------------------------------------

    async def extract_job_description(
        self,
        raw_text: str,
        force_refresh: bool = False,
    ) -> JobProfile:
        """
        Extract structured JobProfile from raw job description text.
        Critically isolates REQUIRED skills from PREFERRED skills.
        """
        text_hash = compute_sha256(raw_text)
        if not force_refresh and text_hash in self._jd_cache:
            logger.info(f"Job profile cache hit (hash={text_hash[:8]})")
            return self._jd_cache[text_hash]

        logger.info(f"Extracting structured JobProfile (text_len={len(raw_text)})")

        profile = None
        ollama_avail = await ollama_service.check_availability()

        if ollama_avail["reachable"]:
            profile = await self._extract_jd_llm(raw_text, text_hash)

        if profile is None:
            logger.info("Using deterministic fallback extraction for job description")
            profile = self._extract_jd_deterministic(raw_text, text_hash)

        self._jd_cache[text_hash] = profile
        return profile

    async def _extract_jd_llm(
        self,
        raw_text: str,
        text_hash: str,
    ) -> Optional[JobProfile]:
        """Query local Ollama to deconstruct the job description into JSON."""
        system_prompt = (
            "You are an expert job description analyzer. Deconstruct the job posting into structured JSON.\n"
            "CRITICAL RULES:\n"
            "1. Strictly separate REQUIRED skills (must-haves, essential) from PREFERRED skills (nice-to-haves, plus, bonus).\n"
            "2. DO NOT treat every mentioned technology as required.\n"
            "3. DO NOT calculate any match scores.\n"
            "4. Return ONLY a single valid JSON object."
        )

        user_prompt = f"""Analyze this job description and output JSON:
---
{raw_text[:6000]}
---

JSON Schema:
{{
  "title": "Job Title",
  "company": "Company Name",
  "location": "Location or Remote",
  "employment_type": "Full-time / Contract / etc",
  "required_skills": ["Python", "FastAPI", "SQL"],
  "preferred_skills": ["Docker", "AWS", "Kubernetes"],
  "responsibilities": ["Design scalable microservices"],
  "education_requirements": ["B.S. in Computer Science or equivalent"],
  "experience_requirements": ["3+ years backend development"],
  "min_years_experience": 3.0,
  "soft_skills": ["Collaboration", "Problem solving"],
  "domain_knowledge": ["FinTech", "Healthcare"]
}}"""

        res = await ollama_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2048,
        )

        if not res["success"]:
            logger.warning(f"Ollama generation failed for JD: {res.get('error')}")
            return None

        parsed_json = extract_json_from_llm_response(res["response_text"])
        if not parsed_json:
            logger.warning("Failed to parse valid JSON from Ollama JD response")
            return None

        try:
            req_skills = [
                skill_normalizer.normalize(s)
                for s in (parsed_json.get("required_skills") or [])
                if s
            ]
            pref_skills = [
                skill_normalizer.normalize(s)
                for s in (parsed_json.get("preferred_skills") or [])
                if s
            ]

            # Categorize requirements
            categorized = RequirementClassifier.classify_requirements_list(
                required_skills=req_skills,
                preferred_skills=pref_skills,
            )

            profile = JobProfile(
                title=parsed_json.get("title") or "Target Position",
                company=parsed_json.get("company") or "Company",
                location=parsed_json.get("location"),
                employment_type=parsed_json.get("employment_type"),
                required_skills=req_skills,
                preferred_skills=pref_skills,
                categorized_requirements=categorized,
                responsibilities=parsed_json.get("responsibilities") or [],
                education_requirements=parsed_json.get("education_requirements") or [],
                experience_requirements=parsed_json.get("experience_requirements") or [],
                min_years_experience=parsed_json.get("min_years_experience"),
                soft_skills=parsed_json.get("soft_skills") or [],
                domain_knowledge=parsed_json.get("domain_knowledge") or [],
                raw_text_hash=text_hash,
                extraction_metadata={
                    "method": "llm",
                    "model": res["model"],
                    "latency_ms": res["latency_ms"],
                },
            )
            return profile
        except Exception as exc:
            logger.warning(f"Error converting parsed JSON to JobProfile: {exc}")
            return None

    def _extract_jd_deterministic(
        self,
        raw_text: str,
        text_hash: str,
    ) -> JobProfile:
        """
        Deterministic regex and catalog parser fallback for job descriptions.
        Distinguishes required vs preferred by looking for section headings.
        """
        lowered = raw_text.lower()
        required_skills: List[str] = []
        preferred_skills: List[str] = []

        # Split into sections if headings exist
        preferred_section_start = -1
        for kw in ["nice to have", "preferred qualification", "bonus point", "preferred skill", "preferred:", "preferred", "plus:", "desired:"]:
            idx = lowered.find(kw)
            if idx != -1:
                preferred_section_start = idx
                break

        if preferred_section_start != -1:
            req_part = raw_text[:preferred_section_start]
            pref_part = raw_text[preferred_section_start:]
            required_skills = [skill_normalizer.normalize(s) for s in skill_normalizer.find_all_known_skills(req_part)]
            preferred_skills = [skill_normalizer.normalize(s) for s in skill_normalizer.find_all_known_skills(pref_part)]
        else:
            all_skills = [skill_normalizer.normalize(s) for s in skill_normalizer.find_all_known_skills(raw_text)]
            required_skills = all_skills[:6]
            preferred_skills = all_skills[6:]

        # Extract min years
        year_match = re.search(r"(\d+)\+?\s*years?(?:\s+of)?\s+experience", lowered)
        min_years = float(year_match.group(1)) if year_match else None

        # Title heuristic
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        title = lines[0] if lines and len(lines[0]) < 80 else "Software Engineer"

        categorized = RequirementClassifier.classify_requirements_list(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
        )

        return JobProfile(
            title=title,
            company="Company",
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            categorized_requirements=categorized,
            min_years_experience=min_years,
            raw_text_hash=text_hash,
            extraction_metadata={"method": "deterministic_fallback"},
        )


# Global singleton instance
extractor_service = ExtractorService()
