import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models import User, Profile, Project, ProjectAnalysis
from backend.app.schemas.profile import ProjectResponse, ProjectCreate, ProjectUpdate, ProjectAnalysisResponse
from backend.app.tasks.celery_app import analyze_github_task

router = APIRouter()

@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).join(Profile).where(
        Profile.user_id == current_user.id
    ).options(selectinload(Project.analysis))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    project = Project(
        profile_id=profile.id,
        **project_in.model_dump()
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).join(Profile).where(
        Project.id == project_id, Profile.user_id == current_user.id
    ).options(selectinload(Project.analysis))
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).join(Profile).where(
        Project.id == project_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    await db.delete(project)
    await db.commit()
    return None

@router.post("/{project_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def trigger_github_analysis(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers GitHub repository analysis as a background task.
    """
    stmt = select(Project).join(Profile).where(
        Project.id == project_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    if not project.github_url:
        raise HTTPException(status_code=400, detail="Project does not contain a GitHub URL.")

    # Dispatch to celery worker
    task = analyze_github_task.delay(str(project.id), str(current_user.id))
    return {
        "message": "GitHub repository analysis has been queued.",
        "task_id": task.id
    }
