import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.core.security import encrypt_api_key
from backend.app.models import User, AIProviderConfig
from backend.app.schemas.auth import AIProviderConfigResponse, AIProviderConfigCreate

router = APIRouter()

@router.get("/configs", response_model=list[AIProviderConfigResponse])
async def list_ai_configs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists user's registered AI model configurations without exposing secret API keys.
    """
    stmt = select(AIProviderConfig).where(AIProviderConfig.user_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/configs", response_model=AIProviderConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_config(
    config_in: AIProviderConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Adds a new model provider configuration with Fernet encrypted keys.
    """
    # Check if this provider exists
    stmt = select(AIProviderConfig).where(
        AIProviderConfig.user_id == current_user.id,
        AIProviderConfig.provider_name == config_in.provider_name
    )
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Configuration for {config_in.provider_name} already exists. Update it instead."
        )

    # Encrypt the API key
    encrypted_key = encrypt_api_key(config_in.api_key)
    
    config = AIProviderConfig(
        user_id=current_user.id,
        provider_name=config_in.provider_name,
        encrypted_api_key=encrypted_key,
        api_base=config_in.api_base,
        is_active=True # Set active by default
    )
    
    # Deactivate other providers if active
    deact_stmt = select(AIProviderConfig).where(
        AIProviderConfig.user_id == current_user.id,
        AIProviderConfig.is_active == True
    )
    deact_res = await db.execute(deact_stmt)
    for c in deact_res.scalars().all():
        c.is_active = False

    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config

@router.put("/configs/{config_id}", response_model=AIProviderConfigResponse)
async def update_ai_config(
    config_id: uuid.UUID,
    config_in: AIProviderConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AIProviderConfig).where(
        AIProviderConfig.id == config_id,
        AIProviderConfig.user_id == current_user.id
    )
    res = await db.execute(stmt)
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="AI Configuration not found.")

    config.provider_name = config_in.provider_name
    config.api_base = config_in.api_base
    if config_in.api_key:
        config.encrypted_api_key = encrypt_api_key(config_in.api_key)
        
    await db.commit()
    return config

@router.post("/configs/{config_id}/activate", response_model=AIProviderConfigResponse)
async def activate_ai_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sets a specific provider to active and deactivates all other configs.
    """
    stmt = select(AIProviderConfig).where(
        AIProviderConfig.id == config_id,
        AIProviderConfig.user_id == current_user.id
    )
    res = await db.execute(stmt)
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="AI Configuration not found.")

    # Deactivate all configs for this user
    all_stmt = select(AIProviderConfig).where(AIProviderConfig.user_id == current_user.id)
    all_res = await db.execute(all_stmt)
    for c in all_res.scalars().all():
        c.is_active = (c.id == config_id)

    await db.commit()
    await db.refresh(config)
    return config

@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AIProviderConfig).where(
        AIProviderConfig.id == config_id,
        AIProviderConfig.user_id == current_user.id
    )
    res = await db.execute(stmt)
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="AI Configuration not found.")

    await db.delete(config)
    await db.commit()
    return None
