"""
Synthetic evaluation fixtures for testing CareerCrew intelligence and matching engine.
CLEARLY LABELED AS SYNTHETIC TEST FIXTURES. NO FABRICATED CLAIMS PRESENTED AS REAL DATA.
Contains 6 synthetic candidate profiles and 4 synthetic job profiles with known ground-truth relationships.
"""

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
from app.services.requirement_classifier import RequirementClassifier


# ==============================================================================
# SYNTHETIC JOB DESCRIPTIONS
# ==============================================================================

# JD 1: Senior Python Backend Developer
JD_SENIOR_PYTHON = JobProfile(
    title="Senior Python Backend Developer",
    company="Synthetic Cloud Labs",
    required_skills=["Python", "FastAPI", "PostgreSQL", "REST API"],
    preferred_skills=["Docker", "AWS", "Redis"],
    responsibilities=[
        "Architect and maintain high-throughput backend microservices using FastAPI and Python.",
        "Design relational database schemas and optimize query performance in PostgreSQL.",
        "Implement secure RESTful APIs with strict automated test coverage.",
    ],
    categorized_requirements=RequirementClassifier.classify_requirements_list(
        required_skills=["Python", "FastAPI", "PostgreSQL", "REST API"],
        preferred_skills=["Docker", "AWS", "Redis"],
    ),
    education_requirements=["B.S. in Computer Science or related engineering field"],
    experience_requirements=["5+ years backend software engineering"],
    min_years_experience=5.0,
    soft_skills=["Mentorship", "System Architecture", "Collaboration"],
    domain_knowledge=["Cloud Computing", "Distributed Systems"],
)

# JD 2: Junior Data Analyst
JD_JUNIOR_DATA = JobProfile(
    title="Junior Data Analyst",
    company="Synthetic Analytics Corp",
    required_skills=["Python", "SQL", "Pandas"],
    preferred_skills=["Tableau", "Machine Learning"],
    responsibilities=[
        "Write SQL queries to extract raw business data and produce recurring reporting dashboards.",
        "Clean and analyze tabular datasets using Python and Pandas.",
    ],
    categorized_requirements=RequirementClassifier.classify_requirements_list(
        required_skills=["Python", "SQL", "Pandas"],
        preferred_skills=["Tableau", "Machine Learning"],
    ),
    education_requirements=["Bachelor's degree in Analytics, Statistics, or CS"],
    min_years_experience=1.0,
)

# JD 3: Embedded C++ Systems Engineer
JD_EMBEDDED_CPP = JobProfile(
    title="Embedded Systems Engineer",
    company="Synthetic Robotics",
    required_skills=["C++", "C", "Linux", "RTOS"],
    preferred_skills=["Bash", "Git"],
    responsibilities=[
        "Develop firmware and real-time control routines in C and C++ for robotic actuators.",
        "Debug hardware timing issues using Linux oscilloscopes and logic analyzers.",
    ],
    categorized_requirements=RequirementClassifier.classify_requirements_list(
        required_skills=["C++", "C", "Linux", "RTOS"],
        preferred_skills=["Bash", "Git"],
    ),
    min_years_experience=4.0,
)


# ==============================================================================
# SYNTHETIC CANDIDATE PROFILES
# ==============================================================================

# Candidate A: Strong Match for Senior Python Backend
CANDIDATE_STRONG_PYTHON = ResumeProfile(
    candidate_name="Alice Smith (Synthetic)",
    contact_info=ContactMetadata(email="alice.synthetic@example.com", location="San Francisco, CA"),
    summary="Principal backend architect with 6 years experience building distributed Python and FastAPI services.",
    skills=SkillsInventory(
        programming_languages=["Python", "SQL", "Bash"],
        frameworks=["FastAPI", "Django"],
        databases=["PostgreSQL", "Redis"],
        cloud_platforms=["AWS", "Docker"],
        tools_and_devops=["Git", "Linux", "CI/CD"],
        soft_skills=["Mentorship", "System Design"],
    ),
    work_experience=[
        WorkExperienceItem(
            organization="Synthetic Tech Corp",
            role="Senior Backend Engineer",
            duration="2020 - Present (4 years)",
            responsibilities=["Designed core REST APIs in FastAPI and managed PostgreSQL clusters."],
            technologies=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
            measurable_achievements=["Scaled API to handle 10,000 req/sec with p99 latency under 25ms."],
        ),
        WorkExperienceItem(
            organization="Alpha Soft",
            role="Software Engineer",
            duration="2018 - 2020 (2 years)",
            responsibilities=["Developed backend services and automated database migrations."],
            technologies=["Python", "PostgreSQL", "AWS"],
            measurable_achievements=["Automated ETL pipeline reducing processing time by 45%."],
        ),
    ],
    projects=[
        ProjectItem(
            name="Distributed Microservices Gateway",
            description="High-throughput API gateway built with Python, FastAPI, and PostgreSQL with Redis caching.",
            technologies=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
            measurable_results=["Processed over 50M requests monthly."],
        )
    ],
    education=[
        EducationItem(
            institution="University of Technology",
            degree="B.S. in Computer Science",
            graduation_year="2018",
        )
    ],
)

# Candidate B: Moderate Match (Has Python & SQL, but lacks FastAPI & Docker)
CANDIDATE_MODERATE_PYTHON = ResumeProfile(
    candidate_name="Bob Miller (Synthetic)",
    contact_info=ContactMetadata(email="bob.synthetic@example.com"),
    summary="Backend developer with 3 years experience in Python and relational databases.",
    skills=SkillsInventory(
        programming_languages=["Python", "SQL"],
        frameworks=["Flask"],
        databases=["PostgreSQL"],
        tools_and_devops=["Git"],
    ),
    work_experience=[
        WorkExperienceItem(
            organization="Beta Solutions",
            role="Software Engineer",
            duration="2021 - Present (3 years)",
            responsibilities=["Maintained internal web portals in Flask and PostgreSQL."],
            technologies=["Python", "Flask", "PostgreSQL"],
        )
    ],
    projects=[
        ProjectItem(
            name="Internal Inventory Tracker",
            description="CRUD management app with Flask and PostgreSQL.",
            technologies=["Python", "PostgreSQL"],
        )
    ],
    education=[
        EducationItem(
            institution="State University",
            degree="B.S. in Information Systems",
        )
    ],
)

# Candidate C: Poor Match for Python (Frontend specialist knowing only React/JS)
CANDIDATE_POOR_MATCH_REACT = ResumeProfile(
    candidate_name="Charlie Davis (Synthetic)",
    contact_info=ContactMetadata(email="charlie.synthetic@example.com"),
    summary="Senior UI/UX frontend engineer specializing in React, Next.js, and CSS styling.",
    skills=SkillsInventory(
        programming_languages=["JavaScript", "TypeScript", "HTML", "CSS"],
        frameworks=["React", "Next.js", "Tailwind CSS"],
        tools_and_devops=["Git", "Figma"],
    ),
    work_experience=[
        WorkExperienceItem(
            organization="Creative Labs",
            role="Frontend Engineer",
            duration="4 years",
            responsibilities=["Built interactive web dashboards and design systems."],
            technologies=["React", "TypeScript", "Tailwind CSS"],
        )
    ],
    projects=[
        ProjectItem(
            name="Design System Component Library",
            description="Accessible React components with Storybook.",
            technologies=["React", "TypeScript"],
        )
    ],
)

# Candidate D: Missing Critical Required Skill (Has Python, FastAPI, Docker, AWS, but zero Database / PostgreSQL)
CANDIDATE_MISSING_POSTGRES = ResumeProfile(
    candidate_name="Dana Scully (Synthetic)",
    contact_info=ContactMetadata(email="dana.synthetic@example.com"),
    summary="FastAPI specialist with cloud expertise.",
    skills=SkillsInventory(
        programming_languages=["Python"],
        frameworks=["FastAPI"],
        cloud_platforms=["AWS", "Docker"],
        tools_and_devops=["Git"],
    ),
    work_experience=[
        WorkExperienceItem(
            organization="Cloud Labs",
            role="Cloud Developer",
            duration="3 years",
            responsibilities=["Deployed containerized Python microservices."],
            technologies=["Python", "FastAPI", "Docker", "AWS"],
        )
    ],
    projects=[
        ProjectItem(
            name="Serverless Event Forwarder",
            description="Event-driven API forwarder using Python and AWS Lambda.",
            technologies=["Python", "FastAPI", "AWS"],
        )
    ],
)

# Candidate E: Missing Preferred Skills (Has ALL required Python, FastAPI, PostgreSQL, REST API; lacks Docker, AWS, Redis)
CANDIDATE_MISSING_PREFERRED = ResumeProfile(
    candidate_name="Edward Nygma (Synthetic)",
    contact_info=ContactMetadata(email="edward.synthetic@example.com"),
    summary="Backend developer with core Python and PostgreSQL fundamentals.",
    skills=SkillsInventory(
        programming_languages=["Python", "SQL"],
        frameworks=["FastAPI"],
        databases=["PostgreSQL"],
    ),
    work_experience=[
        WorkExperienceItem(
            organization="Database Systems Inc",
            role="Software Developer",
            duration="5 years",
            responsibilities=["Created REST APIs in Python with PostgreSQL storage."],
            technologies=["Python", "FastAPI", "PostgreSQL"],
        )
    ],
    projects=[
        ProjectItem(
            name="RESTful Record Archive",
            description="REST API service managing record life cycles.",
            technologies=["Python", "FastAPI", "PostgreSQL"],
        )
    ],
)
