from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.core.limiter import limiter
from backend.app.models import User, JobDescription, AIProviderConfig
from backend.app.schemas.resume import JobDescriptionResponse, JobDescriptionCreate, JDAnalysis
from backend.app.services.ai.factory import ProviderFactory
import logging

logger = logging.getLogger("jd_routes")
router = APIRouter()

@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def analyze_job_description(
    request: Request,
    jd_in: JobDescriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Parses and extracts key skills, requirements, and keywords from a job description.
    """
    if not jd_in.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")

    # Get active AI Provider Config
    stmt = select(AIProviderConfig).where(
        AIProviderConfig.user_id == current_user.id,
        AIProviderConfig.is_active == True
    )
    res = await db.execute(stmt)
    provider_config = res.scalar_one_or_none()

    if not provider_config:
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            from backend.app.core.security import encrypt_api_key
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
        
        # Analyze JD using AI provider
        analysis: JDAnalysis = await ai_provider.analyze_jd(jd_in.jd_text)
        
        # Store in database
        jd_record = JobDescription(
            user_id=current_user.id,
            jd_text=jd_in.jd_text,
            analyzed_skills=list(set(analysis.required_skills + analysis.preferred_skills)),
            analyzed_keywords=analysis.ats_keywords,
            parsed_jd_json=analysis.model_dump()
        )
        
        db.add(jd_record)
        await db.commit()
        await db.refresh(jd_record)
        return jd_record

    except Exception as e:
        logger.error(f"Job Description analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI Job analysis failure: {str(e)}"
        )
