import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import os
from app.core.database import get_db
from app.api.deps import get_current_active_user, check_quota
from app.core.limiter import limiter
from app.models import User, ResumeGeneration, Template, JobDescription
from app.schemas.resume import ResumeGenerationResponse, ResumeGenerationRequest
from app.services.s3_service import s3_service
from app.tasks.celery_app import generate_resume_task

router = APIRouter()

@router.get("", response_model=list[ResumeGenerationResponse])
async def list_resumes(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns user's resume optimization history.
    """
    stmt = select(ResumeGeneration).where(ResumeGeneration.user_id == current_user.id).order_by(
        ResumeGeneration.created_at.desc()
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=ResumeGenerationResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/minute")
async def trigger_resume_generation(
    request: Request,
    body: ResumeGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    quota_check: None = Depends(check_quota("resume")),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a pending resume generation record and queues the PDF assembly pipeline.
    """
    # Verify job description exists
    jd_stmt = select(JobDescription).where(
        JobDescription.id == body.jd_id, JobDescription.user_id == current_user.id
    )
    jd_res = await db.execute(jd_stmt)
    if not jd_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job description not found.")

    # Verify template exists
    tpl_stmt = select(Template).where(
        (Template.id == body.template_id) & 
        ((Template.user_id == None) | (Template.user_id == current_user.id))
    )
    tpl_res = await db.execute(tpl_stmt)
    if not tpl_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="LaTeX template not found.")

    # Save initial pending record
    gen_record = ResumeGeneration(
        user_id=current_user.id,
        jd_id=body.jd_id,
        template_id=body.template_id,
        status="pending",
        generation_metadata=body.generation_metadata or {}
    )
    db.add(gen_record)
    await db.commit()
    await db.refresh(gen_record)

    # Queue Celery task
    generate_resume_task.delay(str(gen_record.id))

    return gen_record

@router.get("/status/{generation_id}", response_model=ResumeGenerationResponse)
async def get_generation_status(
    generation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves execution state of background LaTeX compilation.
    """
    stmt = select(ResumeGeneration).where(
        ResumeGeneration.id == generation_id, ResumeGeneration.user_id == current_user.id
    )
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Resume generation job not found.")
    return record

@router.get("/download/{generation_id}")
async def download_resume_pdf(
    generation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a secure download link for the compiled PDF.
    """
    stmt = select(ResumeGeneration).where(
        ResumeGeneration.id == generation_id, ResumeGeneration.user_id == current_user.id
    )
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Resume generation job not found.")
    
    if record.status != "completed" or not record.pdf_s3_url:
        raise HTTPException(status_code=400, detail="PDF is not compiled yet or compilation failed.")

    # Generate pre-signed URL (lasts 1 hour / 3600 seconds)
    url = await s3_service.get_presigned_url(record.pdf_s3_url, expiration_seconds=3600)
    return {"url": url}

@router.get("/download/local/{file_key:path}")
async def get_local_storage_file(file_key: str):
    """
    Fallback server endpoint serving PDF files stored locally.
    """
    # Basic path traversal guard
    if ".." in file_key or file_key.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file key.")

    local_path = os.path.join(os.getcwd(), "local_storage", file_key)
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Requested file not found in local storage.")
        
    return FileResponse(
        local_path,
        media_type="application/pdf" if file_key.endswith(".pdf") else "application/octet-stream",
        filename=os.path.basename(local_path)
    )
