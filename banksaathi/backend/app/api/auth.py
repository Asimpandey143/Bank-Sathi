"""
Authentication API routes.

POST /api/v1/auth/register — create account
POST /api/v1/auth/login    — return JWT

This is a prototype implementation.
Production systems must use bank-provider approved authentication flows.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password, hash_phone, verify_password
from app.core.errors import ConflictError, UnauthorizedError
from app.database import get_db
from app.models.accessibility_profile import AccessibilityProfile
from app.models.user import User
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    body: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user with phone number and name.

    - Phone is hashed before storage (never stored plaintext)
    - Password is bcrypt-hashed (prototype auth)
    - Accessibility profile is created with defaults
    """
    phone_hash = hash_phone(body.phone)

    # Check for duplicate phone
    existing = await db.execute(select(User).where(User.phone_hash == phone_hash))
    if existing.scalar_one_or_none():
        raise ConflictError("A user with this phone number already exists.")

    user = User(
        phone_hash=phone_hash,
        name=body.name,
        hashed_password=hash_password(body.password),
        role="user",
    )
    db.add(user)
    await db.flush()  # get user.id before creating profile

    # Create default accessibility profile
    profile = AccessibilityProfile(user_id=user.id)
    db.add(profile)

    # Audit
    audit_svc = AuditService(db)
    await audit_svc.log(
        event_type="user.registered",
        actor_user_id=user.id,
        resource_type="user",
        resource_id=user.id,
    )

    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT",
)
async def login(
    body: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login with phone + password, receive a JWT access token.

    The JWT contains only the user_id (sub claim).
    """
    phone_hash = hash_phone(body.phone)

    result = await db.execute(select(User).where(User.phone_hash == phone_hash))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise UnauthorizedError("Invalid phone number or password.")

    token = create_access_token(user.id)

    # Audit login (safe — no credentials logged)
    audit_svc = AuditService(db)
    await audit_svc.log(
        event_type="user.login",
        actor_user_id=user.id,
        resource_type="user",
        resource_id=user.id,
    )

    return TokenResponse(access_token=token)
