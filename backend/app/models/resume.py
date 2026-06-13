from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Integer, JSON, Boolean
import uuid
from backend.app.core.database import TimeStampedBase

class JobDescription(TimeStampedBase):
    __tablename__ = "job_descriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Extracted metadata
    analyzed_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False) # combined required & preferred
    analyzed_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False) # ATS keywords
    parsed_jd_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False) # full JSON representation

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="job_descriptions")
    generations: Mapped[list["ResumeGeneration"]] = relationship(
        "ResumeGeneration", back_populates="job_description", cascade="all, delete-orphan"
    )

class Template(TimeStampedBase):
    __tablename__ = "templates"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True  # Null means system template
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    latex_source: Mapped[str] = mapped_column(Text, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="templates")
    generations: Mapped[list["ResumeGeneration"]] = relationship(
        "ResumeGeneration", back_populates="template"
    )

class ResumeGeneration(TimeStampedBase):
    __tablename__ = "resume_generations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    jd_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, rendering, compiling, completed, failed
    latex_content: Mapped[str] = mapped_column(Text, nullable=True)
    pdf_s3_url: Mapped[str] = mapped_column(String(512), nullable=True)
    tex_s3_url: Mapped[str] = mapped_column(String(512), nullable=True)
    json_s3_url: Mapped[str] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    generation_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    job_description: Mapped["JobDescription"] = relationship("JobDescription", back_populates="generations")
    template: Mapped["Template"] = relationship("Template", back_populates="generations")
    ats_report: Mapped["ATSReport"] = relationship(
        "ATSReport", back_populates="resume_generation", cascade="all, delete-orphan", uselist=False
    )

class ATSReport(TimeStampedBase):
    __tablename__ = "ats_reports"

    resume_generation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resume_generations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    matched_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    weak_sections: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    suggestions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    format_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    action_verb_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ats_reports")
    resume_generation: Mapped["ResumeGeneration"] = relationship("ResumeGeneration", back_populates="ats_report")
