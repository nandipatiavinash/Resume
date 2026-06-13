from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid

# --- Profile Section Schemas ---

class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None

class EducationResponse(EducationBase):
    id: uuid.UUID
    profile_id: uuid.UUID

    class Config:
        from_attributes = True


class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    proficiency: Optional[str] = None

class SkillResponse(SkillBase):
    id: uuid.UUID
    profile_id: uuid.UUID

    class Config:
        from_attributes = True


class ExperienceBase(BaseModel):
    company: str
    position: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    bullets: Optional[List[str]] = None

class ExperienceResponse(ExperienceBase):
    id: uuid.UUID
    profile_id: uuid.UUID

    class Config:
        from_attributes = True


class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    url: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    url: Optional[str] = None

class CertificationResponse(CertificationBase):
    id: uuid.UUID
    profile_id: uuid.UUID

    class Config:
        from_attributes = True


class AchievementBase(BaseModel):
    title: str
    description: str
    date: Optional[str] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

class AchievementResponse(AchievementBase):
    id: uuid.UUID
    profile_id: uuid.UUID

    class Config:
        from_attributes = True


class ProjectAnalysisResponse(BaseModel):
    project_id: uuid.UUID
    summary: str
    bullets: List[str]
    business_impact: str
    complexity_score: int
    technologies: List[str]

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    analysis: Optional[ProjectAnalysisResponse] = None

    class Config:
        from_attributes = True


# --- Master Profile Schema ---

class ProfileBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    summary: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    summary: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    educations: List[EducationResponse] = Field(default_factory=list)
    skills: List[SkillResponse] = Field(default_factory=list)
    experiences: List[ExperienceResponse] = Field(default_factory=list)
    certifications: List[CertificationResponse] = Field(default_factory=list)
    achievements: List[AchievementResponse] = Field(default_factory=list)
    projects: List[ProjectResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
