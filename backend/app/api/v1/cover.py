from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_active_user, check_quota
from app.core.limiter import limiter
from app.models import User, Profile, JobDescription, AIProviderConfig, ResumeGeneration, Project
from app.services.ai.factory import ProviderFactory
from pydantic import BaseModel
import logging

logger = logging.getLogger("cover_letter_routes")
router = APIRouter()

class CoverLetterRequest(BaseModel):
    jd_id: str
    tone: str = "professional"  # professional, enthusiastic, creative, concise

@router.post("/generate", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def generate_cover_letter(
    request: Request,
    body: CoverLetterRequest,
    current_user: User = Depends(get_current_active_user),
    quota_check: None = Depends(check_quota("cover_letter")),
    db: AsyncSession = Depends(get_db)
):
    """
    Assembles a cover letter matching user's profile to analyzed job specifications.
    """
    # 1. Fetch Profile
    prof_stmt = select(Profile).where(Profile.user_id == current_user.id).options(
        selectinload(Profile.educations),
        selectinload(Profile.skills),
        selectinload(Profile.experiences),
        selectinload(Profile.certifications),
        selectinload(Profile.achievements),
        selectinload(Profile.projects).selectinload(Project.analysis)
    )
    prof_res = await db.execute(prof_stmt)
    profile = prof_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Master profile not found. Please create one.")

    # 2. Fetch Job Description
    jd_stmt = select(JobDescription).where(
        JobDescription.id == uuid.UUID(body.jd_id), JobDescription.user_id == current_user.id
    )
    jd_res = await db.execute(jd_stmt)
    jd = jd_res.scalar_one_or_none()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found.")

    # 3. Get active AI Provider Config
    provider_stmt = select(AIProviderConfig).where(
        AIProviderConfig.user_id == current_user.id,
        AIProviderConfig.is_active == True
    )
    provider_res = await db.execute(provider_stmt)
    provider_config = provider_res.scalar_one_or_none()

    if not provider_config:
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            from app.core.security import encrypt_api_key
            encrypted_key = encrypt_api_key(openai_key)
            provider_config = AIProviderConfig(
                provider_name="openai",
                encrypted_api_key=encrypted_key,
                api_base=os.getenv("OPENAI_API_BASE")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active AI Provider API key is missing. Add one in settings."
            )

    try:
        ai_provider = ProviderFactory.get_provider(
            provider_name=provider_config.provider_name,
            encrypted_api_key=provider_config.encrypted_api_key,
            api_base=provider_config.api_base
        )

        # Build raw profile dict
        profile_dict = {
            "full_name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone,
            "website": profile.website,
            "summary": profile.summary,
            "skills": [s.name for s in profile.skills],
            "experience": [
                {
                    "company": ex.company,
                    "position": ex.position,
                    "bullets": ex.bullets
                } for ex in profile.experiences
            ]
        }

        # 4. Generate cover letter
        cover_letter_text = await ai_provider.generate_cover_letter(
            profile_data=profile_dict,
            jd_text=jd.jd_text,
            tone=body.tone
        )

        # 5. Save a ResumeGeneration record for tracking quota & retrieval
        generation = ResumeGeneration(
            user_id=current_user.id,
            jd_id=jd.id,
            status="completed",
            generation_metadata={
                "is_cover_letter": True,
                "cover_letter_content": cover_letter_text,
                "tone": body.tone
            }
        )
        db.add(generation)
        await db.commit()

        return {
            "cover_letter": cover_letter_text,
            "generation_id": generation.id
        }

    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI cover letter generation failed: {str(e)}"
        )

import uuid
