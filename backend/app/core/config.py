import os
from typing import List, Any
from pydantic import AnyHttpUrl, BeforeValidator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def parse_cors_origins(v: str | List[str]) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Resume Intelligence Platform"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_platform"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resume_platform"

    # JWT Security
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption (Fernet key - must be a 32-byte base64-encoded string)
    # Generate one using: cryptography.fernet.Fernet.generate_key().decode()
    ENCRYPTION_KEY: str = "3kR5mR_y6Wk7W5P_l7B1D_g9B2v9f9r7a6S5D4f3g2h=" 

    # Auth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "resume-platform-storage"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Stripe
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Email (SendGrid / SMTP)
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@resumeplatform.com"
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""

    # CORS Whitelist
    BACKEND_CORS_ORIGINS: Annotated[
        Any, BeforeValidator(parse_cors_origins)
    ] = ["http://localhost:3000"]

    # Rate Limiting Settings
    DEFAULT_RATE_LIMIT: str = "100/minute"
    AI_RATE_LIMIT: str = "10/minute"

    @model_validator(mode="after")
    def resolve_database_urls(self) -> "Settings":
        # 1. Standardize schemes first
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
                
        if self.SYNC_DATABASE_URL:
            if self.SYNC_DATABASE_URL.startswith("postgresql+asyncpg://"):
                self.SYNC_DATABASE_URL = self.SYNC_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
            elif self.SYNC_DATABASE_URL.startswith("postgres://"):
                self.SYNC_DATABASE_URL = self.SYNC_DATABASE_URL.replace("postgres://", "postgresql://", 1)

        # 2. Check if either URL points to a local address
        db_is_local = any(h in self.DATABASE_URL for h in ["localhost", "127.0.0.1", "[::1]", "::1"])
        sync_is_local = any(h in self.SYNC_DATABASE_URL for h in ["localhost", "127.0.0.1", "[::1]", "::1"])
        
        # 3. Synchronize cross-references if one is external but the other is local
        if not db_is_local and sync_is_local:
            self.SYNC_DATABASE_URL = self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif not sync_is_local and db_is_local:
            self.DATABASE_URL = self.SYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        return self

settings = Settings()
