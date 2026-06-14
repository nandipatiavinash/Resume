from typing import Generator, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import uuid
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.models import User, Subscription, ResumeGeneration, ATSReport
from app.schemas import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if username is None or token_type != "access":
            raise credentials_exception
        token_data = TokenPayload(sub=username)
    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.id == uuid.UUID(token_data.sub))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

def check_quota(resource_type: str):
    """
    FastAPI Dependency that checks user quotas for the current month.
    resource_type can be: "resume", "ats", "cover_letter"
    """
    async def quota_dependency(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
    ) -> None:
        # Load user subscription
        stmt = select(Subscription).where(Subscription.user_id == current_user.id)
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()
        
        # If user is Pro, allow everything
        if sub and sub.tier.lower() == "pro" and sub.status == "active":
            return

        # Calculate current month start date
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)

        if resource_type == "resume":
            # Count resume generations this month
            gen_stmt = select(ResumeGeneration).where(
                ResumeGeneration.user_id == current_user.id,
                ResumeGeneration.created_at >= start_of_month
            )
            gen_res = await db.execute(gen_stmt)
            count = len(gen_res.scalars().all())
            if count >= 5:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Monthly resume generation limit reached for Free Tier (5/month). Please upgrade to Pro."
                )

        elif resource_type == "ats":
            # Count ATS scans this month
            ats_stmt = select(ATSReport).where(
                ATSReport.user_id == current_user.id,
                ATSReport.created_at >= start_of_month
            )
            ats_res = await db.execute(ats_stmt)
            count = len(ats_res.scalars().all())
            if count >= 5:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Monthly ATS scans limit reached for Free Tier (5/month). Please upgrade to Pro."
                )

        elif resource_type == "cover_letter":
            # Cover letter generations count (stored in ResumeGeneration metadata for tracking)
            # Find all generations with cover letter type this month
            cov_stmt = select(ResumeGeneration).where(
                ResumeGeneration.user_id == current_user.id,
                ResumeGeneration.created_at >= start_of_month
            )
            cov_res = await db.execute(cov_stmt)
            generations = cov_res.scalars().all()
            count = sum(1 for g in generations if g.generation_metadata.get("is_cover_letter") == True)
            if count >= 3:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Monthly cover letter limit reached for Free Tier (3/month). Please upgrade to Pro."
                )
        return

    return quota_dependency
