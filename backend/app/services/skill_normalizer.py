"""
Deterministic skill normalization and alias resolution layer.
Enforces strict canonical representation without false equivalences
(e.g., JavaScript == JS != Java; C != C++ != C#).
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from app.schemas.intelligence import SkillCategory


# Canonical Skill -> List of lower-cased aliases/variations
SKILL_CATALOG: Dict[str, Dict[str, Any]] = {
    # Programming Languages
    "JavaScript": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["javascript", "js", "ecmascript", "es6", "vanilla javascript", "vanilla js"],
    },
    "TypeScript": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["typescript", "ts"],
    },
    "Python": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["python", "python3", "python 3", "python2", "py"],
    },
    "Java": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["java", "java core", "core java", "java 17", "java 11", "java 8", "java 21"],
    },
    "C": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["c", "c language"],
    },
    "C++": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["c++", "cpp", "c plus plus"],
    },
    "C#": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["c#", "csharp", "c sharp", ".net c#"],
    },
    "Go": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["go", "golang", "go language"],
    },
    "Rust": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["rust", "rust-lang"],
    },
    "Ruby": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["ruby"],
    },
    "PHP": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["php", "php8", "php7"],
    },
    "Kotlin": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["kotlin"],
    },
    "Swift": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["swift"],
    },
    "SQL": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["sql", "structured query language", "ansi sql"],
    },
    "HTML": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["html", "html5"],
    },
    "CSS": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["css", "css3"],
    },
    "Bash": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["bash", "shell", "shell scripting", "sh", "zsh"],
    },

    # Frameworks & Runtimes
    "Node.js": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["nodejs", "node.js", "node", "node js"],
    },
    "React": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["react", "reactjs", "react.js", "react native"],
    },
    "Next.js": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["nextjs", "next.js", "next js", "next"],
    },
    "Vue.js": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["vue", "vuejs", "vue.js", "vue 3"],
    },
    "Angular": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["angular", "angularjs", "angular 2+"],
    },
    "FastAPI": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["fastapi", "fast-api", "fast api"],
    },
    "Django": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["django", "django rest framework", "drf"],
    },
    "Flask": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["flask"],
    },
    "Express.js": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["express", "expressjs", "express.js"],
    },
    "Spring Boot": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["spring boot", "springboot", "spring", "spring framework"],
    },
    ".NET": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": [".net", ".net core", "asp.net", "dotnet"],
    },
    "Tailwind CSS": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["tailwind", "tailwindcss", "tailwind css"],
    },
    "CrewAI": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["crewai", "crew-ai", "crew ai"],
    },
    "LangChain": {
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["langchain", "lang-chain"],
    },

    # Databases
    "PostgreSQL": {
        "category": SkillCategory.DATABASE,
        "aliases": ["postgresql", "postgres", "psql", "pgsql", "postgresql db"],
    },
    "MySQL": {
        "category": SkillCategory.DATABASE,
        "aliases": ["mysql", "my-sql"],
    },
    "MongoDB": {
        "category": SkillCategory.DATABASE,
        "aliases": ["mongodb", "mongo", "mongo db"],
    },
    "SQLite": {
        "category": SkillCategory.DATABASE,
        "aliases": ["sqlite", "sqlite3"],
    },
    "Redis": {
        "category": SkillCategory.DATABASE,
        "aliases": ["redis", "redis cache"],
    },
    "Elasticsearch": {
        "category": SkillCategory.DATABASE,
        "aliases": ["elasticsearch", "elastic search", "opensearch"],
    },
    "ChromaDB": {
        "category": SkillCategory.DATABASE,
        "aliases": ["chromadb", "chroma", "chroma db"],
    },
    "FAISS": {
        "category": SkillCategory.DATABASE,
        "aliases": ["faiss"],
    },
    "Cassandra": {
        "category": SkillCategory.DATABASE,
        "aliases": ["cassandra", "apache cassandra"],
    },
    "DynamoDB": {
        "category": SkillCategory.DATABASE,
        "aliases": ["dynamodb", "dynamo db", "aws dynamodb"],
    },

    # Cloud & DevOps
    "AWS": {
        "category": SkillCategory.CLOUD,
        "aliases": ["aws", "amazon web services", "amazon aws"],
    },
    "Google Cloud Platform": {
        "category": SkillCategory.CLOUD,
        "aliases": ["gcp", "google cloud", "google cloud platform"],
    },
    "Microsoft Azure": {
        "category": SkillCategory.CLOUD,
        "aliases": ["azure", "microsoft azure", "ms azure"],
    },
    "Docker": {
        "category": SkillCategory.DEVOPS,
        "aliases": ["docker", "docker container", "docker containers", "docker compose"],
    },
    "Kubernetes": {
        "category": SkillCategory.DEVOPS,
        "aliases": ["kubernetes", "k8s"],
    },
    "CI/CD": {
        "category": SkillCategory.DEVOPS,
        "aliases": ["ci/cd", "cicd", "continuous integration", "ci cd", "github actions", "gitlab ci", "jenkins"],
    },
    "Terraform": {
        "category": SkillCategory.DEVOPS,
        "aliases": ["terraform", "iac", "infrastructure as code"],
    },
    "Linux": {
        "category": SkillCategory.DEVOPS,
        "aliases": ["linux", "unix", "ubuntu", "debian", "centos", "rhel"],
    },

    # Architecture & Concepts
    "REST API": {
        "category": SkillCategory.ARCHITECTURE,
        "aliases": ["rest api", "rest", "restful", "restful api", "rest apis", "restful apis"],
    },
    "GraphQL": {
        "category": SkillCategory.ARCHITECTURE,
        "aliases": ["graphql", "graph-ql", "graph ql"],
    },
    "Microservices": {
        "category": SkillCategory.ARCHITECTURE,
        "aliases": ["microservices", "microservice", "microservice architecture"],
    },
    "Ollama": {
        "category": SkillCategory.TOOL,
        "aliases": ["ollama", "local ollama"],
    },
    "Git": {
        "category": SkillCategory.TOOL,
        "aliases": ["git", "github", "gitlab", "version control", "git version control"],
    },
    "PyMuPDF": {
        "category": SkillCategory.LIBRARY,
        "aliases": ["pymupdf", "fitz"],
    },
    "Unit Testing": {
        "category": SkillCategory.TESTING,
        "aliases": ["unit testing", "pytest", "jest", "junit", "tdd", "test driven development"],
    },
    "Machine Learning": {
        "category": SkillCategory.DOMAIN,
        "aliases": ["machine learning", "ml", "deep learning", "ai", "artificial intelligence"],
    },
    "Natural Language Processing": {
        "category": SkillCategory.DOMAIN,
        "aliases": ["nlp", "natural language processing", "llm", "large language models"],
    },
}


class SkillNormalizer:
    """
    Deterministic resolution engine that maps diverse skill tokens to canonical representations
    while strictly preserving semantic boundaries (e.g. Java vs JavaScript).
    """

    def __init__(self):
        self._alias_to_canonical: Dict[str, str] = {}
        self._canonical_to_category: Dict[str, SkillCategory] = {}
        self._build_lookup_tables()

    def _build_lookup_tables(self) -> None:
        for canonical, info in SKILL_CATALOG.items():
            cat = info.get("category", SkillCategory.OTHER)
            self._canonical_to_category[canonical] = cat

            # Canonical itself resolves to canonical
            self._alias_to_canonical[canonical.lower().strip()] = canonical

            # All aliases resolve to canonical
            for alias in info.get("aliases", []):
                self._alias_to_canonical[alias.lower().strip()] = canonical

    @staticmethod
    def _clean_token(token: str) -> str:
        """Strip surrounding punctuation while preserving meaningful internal chars (+, #, .)."""
        if not token:
            return ""
        t = token.strip().lower()
        # Remove trailing commas, semicolons, parentheses
        t = re.sub(r"^[\s,\.;\(\)\[\]]+|[\s,\.;\(\)\[\]]+$", "", t)
        return t

    def normalize(self, skill_text: str) -> str:
        """
        Map any skill string to its canonical equivalent if known.
        Returns cleaned original title-cased string if no canonical alias exists.
        """
        if not skill_text or not skill_text.strip():
            return ""

        clean = self._clean_token(skill_text)
        if not clean:
            return ""

        # 1. Exact alias match
        if clean in self._alias_to_canonical:
            return self._alias_to_canonical[clean]

        # 2. Handle common punctuation variations e.g. "postgres-db" -> "postgres db"
        space_var = clean.replace("-", " ").replace("_", " ")
        if space_var in self._alias_to_canonical:
            return self._alias_to_canonical[space_var]

        # 3. Handle dot-separated variations like "node js" vs "nodejs"
        no_dot = clean.replace(".", "")
        if no_dot in self._alias_to_canonical:
            return self._alias_to_canonical[no_dot]

        # Return cleaned version if unrecognized
        # Format neatly: if single word, titlecase; preserve capitalization if mixed
        original = skill_text.strip()
        return original

    def get_category(self, skill_name: str) -> SkillCategory:
        """Retrieve category for a canonical or alias skill name."""
        canonical = self.normalize(skill_name)
        return self._canonical_to_category.get(canonical, SkillCategory.OTHER)

    def are_equivalent(self, skill1: str, skill2: str) -> bool:
        """
        Deterministic equivalence check.
        Ensures strict boundary checks:
        are_equivalent('JavaScript', 'JS') -> True
        are_equivalent('Java', 'JavaScript') -> False
        """
        norm1 = self.normalize(skill1)
        norm2 = self.normalize(skill2)
        if not norm1 or not norm2:
            return False
        return norm1.lower() == norm2.lower()

    def find_all_known_skills(self, text: str) -> List[str]:
        """
        Deterministic scan of raw text against canonical catalog.
        Finds occurrences using word boundary matching.
        """
        found: Set[str] = set()
        lowered_text = f" {text.lower()} "

        # Prioritize multi-word aliases first to prevent partial overlaps
        # e.g., match "amazon web services" before "web"
        all_aliases = sorted(self._alias_to_canonical.keys(), key=len, reverse=True)

        for alias in all_aliases:
            canonical = self._alias_to_canonical[alias]
            if canonical in found:
                continue

            # Word boundary regex with special char handling for C++, C#, .NET
            escaped = re.escape(alias)
            pattern = rf"(?:\b|\s|^){escaped}(?:\b|\s|$|[,\.;:\)])"
            if re.search(pattern, lowered_text):
                found.add(canonical)

        return sorted(list(found))


# Global singleton instance
skill_normalizer = SkillNormalizer()
