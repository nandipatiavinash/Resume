import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models import User, Subscription, ResumeGeneration, Profile, AIProviderConfig
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger("admin_routes")

class SubscriptionOverrideRequest(BaseModel):
    tier: str  # free, pro
    status: str = "active"

@router.get("/users")
async def admin_list_users(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns list of all users and their subscription details.
    """
    stmt = select(User).options(selectinload(User.subscription))
    res = await db.execute(stmt)
    users = res.scalars().all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "subscription": {
                "tier": u.subscription.tier,
                "status": u.subscription.status,
                "current_period_end": u.subscription.current_period_end
            } if u.subscription else None
        } for u in users
    ]

@router.get("/analytics")
async def get_system_analytics(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates key platform performance metrics.
    """
    # 1. Total Users
    users_stmt = select(func.count(User.id))
    users_res = await db.execute(users_stmt)
    total_users = users_res.scalar_one()

    # 2. Total Resume Generations
    gens_stmt = select(func.count(ResumeGeneration.id))
    gens_res = await db.execute(gens_stmt)
    total_resumes = gens_res.scalar_one()

    # 3. Active Pro Subscriptions
    pro_stmt = select(func.count(Subscription.id)).where(
        Subscription.tier == "pro",
        Subscription.status == "active"
    )
    pro_res = await db.execute(pro_stmt)
    active_pro_subscriptions = pro_res.scalar_one()

    # 4. AI Provider configs count
    providers_stmt = select(AIProviderConfig.provider_name, func.count(AIProviderConfig.id)).group_by(
        AIProviderConfig.provider_name
    )
    providers_res = await db.execute(providers_stmt)
    provider_distribution = {name: count for name, count in providers_res.all()}

    return {
        "total_users": total_users,
        "total_resumes_generated": total_resumes,
        "active_pro_users": active_pro_subscriptions,
        "ai_provider_adoption": provider_distribution
    }

@router.put("/users/{user_id}/subscription")
async def override_user_subscription(
    user_id: uuid.UUID,
    body: SubscriptionOverrideRequest,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Allows admin to manually override a user's subscription settings.
    """
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    res = await db.execute(stmt)
    sub = res.scalar_one_or_none()
    if not sub:
        # Create one if missing
        sub = Subscription(
            user_id=user_id,
            tier=body.tier,
            status=body.status
        )
        db.add(sub)
    else:
        sub.tier = body.tier
        sub.status = body.status
        
    await db.commit()
    return {
        "message": f"Successfully updated subscription details for user {user_id}",
        "tier": sub.tier,
        "status": sub.status
    }
