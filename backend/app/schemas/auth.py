from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

# --- AI Provider Configuration Schemas ---
class AIProviderConfigCreate(BaseModel):
    provider_name: str  # openai, claude, gemini, deepseek, openrouter
    api_key: str
    api_base: Optional[str] = None

class AIProviderConfigResponse(BaseModel):
    id: uuid.UUID
    provider_name: str
    api_base: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
