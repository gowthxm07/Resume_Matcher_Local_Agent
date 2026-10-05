"""
Core application configuration for CareerCrew.
Follows a strict privacy-first, local-only architecture with zero paid cloud APIs.
"""

from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Determine repository root (two levels up from backend/app/core -> backend -> root)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), str(PROJECT_ROOT / ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core Application Settings
    APP_NAME: str = "CareerCrew Backend"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Local LLM Provider (Ollama only - no external paid APIs permitted)
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_REQUEST_TIMEOUT: float = 120.0

    # Local SQLite Database
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'database' / 'careercrew.db'}"

    # Storage Paths
    DATA_DIR: Path = Field(default_factory=lambda: PROJECT_ROOT / "data")
    UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB limit for documents
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]

    # Local Vector Store Configuration
    VECTOR_STORE_TYPE: str = "chroma"
    VECTOR_STORE_DIR: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "data" / "embeddings" / "chroma"
    )

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_local_provider_only(cls, v: str) -> str:
        """Enforce strict local-only policy against cloud LLM providers."""
        prohibited = ["openai", "anthropic", "gemini", "bedrock", "azure", "cohere"]
        normalized = v.lower().strip()
        if any(cloud_provider in normalized for cloud_provider in prohibited):
            raise ValueError(
                f"Cloud provider '{v}' is prohibited by CareerCrew privacy architecture. "
                "Only local providers (e.g., 'ollama') are supported."
            )
        return normalized

    @property
    def resumes_dir(self) -> Path:
        """Directory for stored resume files."""
        path = self.DATA_DIR / "resumes"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def job_descriptions_dir(self) -> Path:
        """Directory for stored job descriptions."""
        path = self.DATA_DIR / "job_descriptions"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def projects_dir(self) -> Path:
        """Directory for stored project evidence files."""
        path = self.DATA_DIR / "projects"
        path.mkdir(parents=True, exist_ok=True)
        return path


# Singleton settings instance
settings = Settings()
