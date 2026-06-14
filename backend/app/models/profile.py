from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Integer, Date, JSON
import uuid
from app.core.database import TimeStampedBase

class Profile(TimeStampedBase):
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(255), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    educations: Mapped[list["Education"]] = relationship(
        "Education", back_populates="profile", cascade="all, delete-orphan"
    )
    skills: Mapped[list["Skill"]] = relationship(
        "Skill", back_populates="profile", cascade="all, delete-orphan"
    )
    experiences: Mapped[list["Experience"]] = relationship(
        "Experience", back_populates="profile", cascade="all, delete-orphan"
    )
    certifications: Mapped[list["Certification"]] = relationship(
        "Certification", back_populates="profile", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        "Achievement", back_populates="profile", cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="profile", cascade="all, delete-orphan"
    )

class Education(TimeStampedBase):
    __tablename__ = "education"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[str] = mapped_column(String(50), nullable=True) # string formatted or date representation
    end_date: Mapped[str] = mapped_column(String(50), nullable=True)   # Present or string
    gpa: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="educations")

class Skill(TimeStampedBase):
    __tablename__ = "skills"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)  # Languages, Frameworks, Libraries, Tools
    proficiency: Mapped[str] = mapped_column(String(50), nullable=True)  # Beginner, Intermediate, Expert

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="skills")

class Experience(TimeStampedBase):
    __tablename__ = "experience"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str] = mapped_column(String(50), nullable=False)
    end_date: Mapped[str] = mapped_column(String(50), nullable=True)  # Present or string
    description: Mapped[str] = mapped_column(Text, nullable=True)
    bullets: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False) # list of bullet points

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="experiences")

class Certification(TimeStampedBase):
    __tablename__ = "certifications"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[str] = mapped_column(String(50), nullable=True)
    expiration_date: Mapped[str] = mapped_column(String(50), nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="certifications")

class Achievement(TimeStampedBase):
    __tablename__ = "achievements"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="achievements")

class Project(TimeStampedBase):
    __tablename__ = "projects"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str] = mapped_column(String(50), nullable=True)
    end_date: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="projects")
    analysis: Mapped["ProjectAnalysis"] = relationship(
        "ProjectAnalysis", back_populates="project", cascade="all, delete-orphan", uselist=False
    )

class ProjectAnalysis(TimeStampedBase):
    __tablename__ = "project_analysis"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)  # 2-sentence summary
    bullets: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)  # 4-6 ATS bullets
    business_impact: Mapped[str] = mapped_column(Text, nullable=False)  # impact statement
    complexity_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1-10
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)  # technology tags

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="analysis")
