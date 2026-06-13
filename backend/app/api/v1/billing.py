from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.core.config import settings
from backend.app.models import User, Subscription
from backend.app.services.stripe_service import stripe_service
from pydantic import BaseModel
from datetime import datetime
import json
import logging

router = APIRouter()
logger = logging.getLogger("billing_routes")

class CheckoutRequest(BaseModel):
    plan_type: str = "pro" # pro

@router.post("/checkout")
async def create_billing_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a Stripe billing checkout session URL for upgrading to Pro tier.
    """
    success_url = f"{settings.BACKEND_CORS_ORIGINS[0]}/dashboard"
    cancel_url = f"{settings.BACKEND_CORS_ORIGINS[0]}/settings"
    
    try:
        checkout_url = await stripe_service.create_checkout_session(
            user_id=str(current_user.id),
            email=current_user.email,
            plan_type=body.plan_type,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return {"checkout_url": checkout_url}
    except Exception as e:
        logger.error(f"Checkout generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Billing service error: {str(e)}")

@router.post("/webhook")
async def stripe_webhook_endpoint(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Listens to Stripe events to activate or cancel subscriptions in real-time.
    """
    payload = await request.body()
    
    try:
        event = stripe_service.construct_event(payload, stripe_signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not event:
        raise HTTPException(status_code=400, detail="Signature verification failed.")

    logger.info(f"Received Stripe Webhook event: {event.type}")
    
    # Process event
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        plan = session.metadata.get("plan", "pro")
        customer_id = session.customer
        subscription_id = session.subscription

        if user_id:
            # Upgrade user subscription
            stmt = select(Subscription).where(Subscription.user_id == uuid_from_str(user_id))
            res = await db.execute(stmt)
            sub = res.scalar_one_or_none()
            
            # Convert timestamp to datetime
            current_period_end = None
            if session.get("expires_at"):
                current_period_end = datetime.utcfromtimestamp(session.expires_at)
            
            if not sub:
                sub = Subscription(
                    user_id=uuid_from_str(user_id),
                    tier=plan,
                    status="active",
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    current_period_end=current_period_end
                )
                db.add(sub)
            else:
                sub.tier = plan
                sub.status = "active"
                sub.stripe_customer_id = customer_id
                sub.stripe_subscription_id = subscription_id
                sub.current_period_end = current_period_end
            
            await db.commit()
            logger.info(f"User {user_id} upgraded to {plan} subscription.")

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        subscription_id = subscription.id
        
        # Revoke access / reset to free
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        res = await db.execute(stmt)
        sub = res.scalar_one_or_none()
        
        if sub:
            sub.tier = "free"
            sub.status = "canceled"
            await db.commit()
            logger.info(f"Subscription {subscription_id} was deleted. User reset to free tier.")

    return {"status": "success"}

def uuid_from_str(val: str) -> uuid.UUID:
    import uuid
    return uuid.UUID(val)
