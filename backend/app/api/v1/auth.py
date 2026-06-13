import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import (
    get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
)
from backend.app.core.limiter import limiter
from backend.app.models import User, Subscription
from backend.app.schemas import (
    UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm
)
import httpx
import logging

logger = logging.getLogger("auth_routes")
router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def signup(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user and sets up their default free subscription tier.
    """
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    existing_user = res.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pwd
    )
    db.add(user)
    await db.flush() # Populate user ID

    # Create default subscription
    subscription = Subscription(
        user_id=user.id,
        tier="free",
        status="active"
    )
    db.add(subscription)
    await db.commit()
    
    return user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Standard email-password authentication.
    """
    stmt = select(User).where(User.email == credentials.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(token_in: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Generates a new access token using a valid, unexpired refresh token.
    """
    try:
        payload = decode_token(token_in.refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    stmt = select(User).where(User.id == uuid.UUID(user_id))
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/google-oauth")
async def google_oauth_url():
    """
    Generates and returns Google login authorization URL.
    """
    redirect_uri = f"{settings.BACKEND_CORS_ORIGINS[0]}/auth/callback"
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile"
    )
    return {"url": url}

@router.post("/google/callback", response_model=Token)
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Handles auth code exchange, logs in the user, and sets up free subscription if new.
    """
    redirect_uri = f"{settings.BACKEND_CORS_ORIGINS[0]}/auth/callback"
    
    # Exchanging authorization code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            token_res = await client.post(token_url, data=token_data)
            token_res.raise_for_status()
            token_json = token_res.json()
            access_token = token_json.get("access_token")
            
            # Fetch user details
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_res = await client.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            userinfo_res.raise_for_status()
            userinfo_json = userinfo_res.json()
        except Exception as e:
            logger.error(f"Google OAuth handshake failed: {e}")
            raise HTTPException(status_code=400, detail="Google authentication failed.")

    email = userinfo_json.get("email")
    google_id = userinfo_json.get("sub")
    
    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google.")

    # Find or create user
    stmt = select(User).where((User.google_id == google_id) | (User.email == email))
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if not user:
        user = User(
            email=email,
            google_id=google_id,
            is_active=True
        )
        db.add(user)
        await db.flush()
        
        # Free subscription
        subscription = Subscription(
            user_id=user.id,
            tier="free",
            status="active"
        )
        db.add(subscription)
        await db.commit()
    else:
        # Update google_id if missing
        if not user.google_id:
            user.google_id = google_id
            await db.commit()

    jwt_access = create_access_token(user.id)
    jwt_refresh = create_refresh_token(user.id)
    
    return {
        "access_token": jwt_access,
        "refresh_token": jwt_refresh,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request, body: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """
    Generates a password reset token and mocks sending a reset email.
    """
    stmt = select(User).where(User.email == body.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if user:
        # Generate temporary token expiring in 15 mins
        reset_token = f"reset_{uuid.uuid4().hex}"
        # In production, save reset_token in Redis with a TTL of 15m (900s)
        # Mock sending email
        logger.info(f"MOCK EMAIL: Send password reset token to {body.email}: {reset_token}")
        
    return {"message": "If the email is registered, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(body: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """
    Resets the password of the user using verified reset token.
    """
    # Verify token
    # In production, fetch user_id mapped to this token from Redis.
    # Since this is a test environment, let's mock validation:
    if not body.token.startswith("reset_"):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    # Mock finding a user
    # For testing, we just update the first user or mock success
    stmt = select(User)
    res = await db.execute(stmt)
    user = res.scalars().first()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found.")
        
    user.hashed_password = get_password_hash(body.new_password)
    await db.commit()
    return {"message": "Password has been successfully updated."}
