from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid

# --- Profile schemas (used for resume content formatting) ---
class EducationContent(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None

class SkillContent(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None

class ExperienceContent(BaseModel):
    company: str
    position: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class CertificationContent(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    url: Optional[str] = None

class AchievementContent(BaseModel):
    title: str
    description: str
    date: Optional[str] = None

class ProjectContent(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

# --- JD analysis schemas ---
class JDAnalysis(BaseModel):
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    ats_keywords: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    role_summary: str = ""

# --- ResumeContent schema (the output of generation) ---
class ResumeContent(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    summary: str
    education: List[EducationContent] = Field(default_factory=list)
    skills: List[SkillContent] = Field(default_factory=list)
    experience: List[ExperienceContent] = Field(default_factory=list)
    certifications: List[CertificationContent] = Field(default_factory=list)
    achievements: List[AchievementContent] = Field(default_factory=list)
    projects: List[ProjectContent] = Field(default_factory=list)

# --- API Request/Response schemas ---
class JobDescriptionCreate(BaseModel):
    jd_text: str

class JobDescriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    jd_text: str
    analyzed_skills: List[str]
    analyzed_keywords: List[str]
    parsed_jd_json: dict

    class Config:
        from_attributes = True

class ResumeGenerationRequest(BaseModel):
    jd_id: uuid.UUID
    template_id: uuid.UUID
    generation_metadata: Optional[dict] = Field(default_factory=dict)

class ResumeGenerationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    jd_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    status: str
    pdf_s3_url: Optional[str] = None
    tex_s3_url: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class ATSReportResponse(BaseModel):
    resume_generation_id: uuid.UUID
    score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    weak_sections: List[str]
    suggestions: List[str]
    format_score: int
    action_verb_score: int

    class Config:
        from_attributes = True

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    latex_source: str

class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_custom: bool

    class Config:
        from_attributes = True
