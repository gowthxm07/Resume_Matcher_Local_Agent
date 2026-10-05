"""
Pydantic schemas for core CareerCrew database entities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# Resume Schemas
class ResumeBase(BaseModel):
    filename: str
    file_type: str
    status: str = "uploaded"


class ResumeCreate(ResumeBase):
    raw_text: str = ""
    file_path: str
    file_size_bytes: int = 0
    parsed_metadata: Dict[str, Any] = Field(default_factory=dict)


class ResumeResponse(ResumeBase):
    id: str
    file_size_bytes: int
    char_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Job Description Schemas
class JobDescriptionBase(BaseModel):
    title: str = "Untitled Position"
    company: str = "Unknown Company"
    source_url: Optional[str] = None
    status: str = "pending"


class JobDescriptionCreate(JobDescriptionBase):
    raw_text: str
    parsed_metadata: Dict[str, Any] = Field(default_factory=dict)


class JobDescriptionResponse(JobDescriptionBase):
    id: str
    char_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: str = ""
    repo_path: str
    status: str = "pending"


class ProjectCreate(ProjectBase):
    evidence_metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Application Schemas
class ApplicationBase(BaseModel):
    target_role: str
    company_name: str
    status: str = "draft"
    notes: Optional[str] = ""


class ApplicationCreate(ApplicationBase):
    resume_id: str
    job_description_id: str


class ApplicationResponse(ApplicationBase):
    id: str
    resume_id: str
    job_description_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Analysis Run Schemas
class AnalysisRunBase(BaseModel):
    run_type: str = "initial_assessment"
    status: str = "pending"


class AnalysisRunCreate(AnalysisRunBase):
    resume_id: str
    job_description_id: str
    application_id: Optional[str] = None


class AnalysisRunResponse(AnalysisRunBase):
    id: str
    resume_id: str
    job_description_id: str
    application_id: Optional[str]
    match_score: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    model_config = ConfigDict(from_attributes=True)

