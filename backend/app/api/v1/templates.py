import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, Template
from app.schemas.resume import TemplateResponse, TemplateCreate

router = APIRouter()

async def initialize_system_templates(db: AsyncSession) -> None:
    """
    Checks if system templates exist, and registers them from templates/ directory if missing.
    """
    stmt = select(Template).where(Template.user_id == None)
    res = await db.execute(stmt)
    if len(res.scalars().all()) > 0:
        return

    templates_dir = os.path.join(os.getcwd(), "templates")
    default_templates = [
        {"name": "jake_resume", "desc": "Jake Resume (single-column, clean, highly readable)"},
        {"name": "deedy_resume", "desc": "Deedy Resume (two-column, side-panel layout)"},
        {"name": "awesome_cv", "desc": "Awesome CV (color accented headers, professional style)"},
        {"name": "modern_cv", "desc": "Modern CV (minimalist styling with generous white space)"}
    ]

    for dt in default_templates:
        file_path = os.path.join(templates_dir, f"{dt['name']}.tex")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            template = Template(
                name=dt["name"],
                description=dt["desc"],
                latex_source=content,
                is_custom=False,
                user_id=None
            )
            db.add(template)
    
    await db.commit()

@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns available resume templates (default system templates + custom ones).
    """
    # Self-healing setup: Populate default templates if database table is empty
    await initialize_system_templates(db)
    
    stmt = select(Template).where(
        (Template.user_id == None) | (Template.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def upload_custom_template(
    template_in: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads a new user-customized LaTeX template.
    """
    template = Template(
        user_id=current_user.id,
        name=template_in.name,
        description=template_in.description,
        latex_source=template_in.latex_source,
        is_custom=True
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_by_id(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Template).where(
        (Template.id == template_id) & 
        ((Template.user_id == None) | (Template.user_id == current_user.id))
    )
    res = await db.execute(stmt)
    template = res.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found.")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_custom_template(
    template_id: uuid.UUID,
    template_in: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Template).where(
        Template.id == template_id, Template.user_id == current_user.id
    )
    res = await db.execute(stmt)
    template = res.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Custom template not found or unauthorized.")

    template.name = template_in.name
    template.description = template_in.description
    template.latex_source = template_in.latex_source
    await db.commit()
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Template).where(
        Template.id == template_id, Template.user_id == current_user.id
    )
    res = await db.execute(stmt)
    template = res.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Custom template not found or unauthorized.")

    await db.delete(template)
    await db.commit()
    return None
