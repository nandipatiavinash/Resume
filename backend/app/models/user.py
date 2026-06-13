from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from datetime import datetime
import uuid
from backend.app.core.database import TimeStampedBase

class User(TimeStampedBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)  # Nullable for OAuth
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)

    # Relationships
    subscription: Mapped["Subscription"] = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    provider_configs: Mapped[list["AIProviderConfig"]] = relationship(
        "AIProviderConfig", back_populates="user", cascade="all, delete-orphan"
    )
    job_descriptions: Mapped[list["JobDescription"]] = relationship(
        "JobDescription", back_populates="user", cascade="all, delete-orphan"
    )
    resumes: Mapped[list["ResumeGeneration"]] = relationship(
        "ResumeGeneration", back_populates="user", cascade="all, delete-orphan"
    )
    ats_reports: Mapped[list["ATSReport"]] = relationship(
        "ATSReport", back_populates="user", cascade="all, delete-orphan"
    )
    templates: Mapped[list["Template"]] = relationship(
        "Template", back_populates="user", cascade="all, delete-orphan"
    )

class Subscription(TimeStampedBase):
    __tablename__ = "subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    tier: Mapped[str] = mapped_column(String(50), default="free", nullable=False)  # free, pro
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, trialing, canceled, past_due

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")

class AIProviderConfig(TimeStampedBase):
    __tablename__ = "ai_providers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)  # openai, claude, gemini, deepseek, openrouter
    encrypted_api_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    api_base: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="provider_configs")

    __table_args__ = (
        Index("idx_user_provider", "user_id", "provider_name", unique=True),
    )
