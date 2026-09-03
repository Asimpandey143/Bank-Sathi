"""
User API routes.

GET  /api/v1/users/me              — get profile + accessibility prefs
PATCH /api/v1/users/me/preferences — update accessibility preferences
GET  /api/v1/users/me/beneficiaries — list user's beneficiaries
POST /api/v1/users/me/beneficiaries — add a beneficiary
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.security import get_current_user
from app.database import get_db
from app.models.accessibility_profile import AccessibilityProfile
from app.models.beneficiary import Beneficiary
from app.models.user import User
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryResponse
from app.schemas.user import (
    AccessibilityPreferencesUpdate,
    AccessibilityProfileResponse,
    UserResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.get(
    "/me/preferences",
    response_model=AccessibilityProfileResponse,
    summary="Get accessibility preferences",
)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AccessibilityProfileResponse:
    result = await db.execute(
        select(AccessibilityProfile).where(
            AccessibilityProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Accessibility profile")
    return AccessibilityProfileResponse.model_validate(profile)


@router.patch(
    "/me/preferences",
    response_model=AccessibilityProfileResponse,
    summary="Update accessibility preferences",
)
async def update_preferences(
    body: AccessibilityPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AccessibilityProfileResponse:
    """Update the user's accessibility preferences."""
    result = await db.execute(
        select(AccessibilityProfile).where(
            AccessibilityProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        # Create if missing
        profile = AccessibilityProfile(user_id=current_user.id)
        db.add(profile)

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    audit_svc = AuditService(db)
    await audit_svc.log(
        event_type="user.preferences_updated",
        actor_user_id=current_user.id,
        resource_type="accessibility_profile",
        resource_id=current_user.id,
        metadata={"updated_fields": list(update_data.keys())},
    )

    await db.commit()
    await db.refresh(profile)
    return AccessibilityProfileResponse.model_validate(profile)


@router.get(
    "/me/beneficiaries",
    response_model=list[BeneficiaryResponse],
    summary="List beneficiaries",
)
async def list_beneficiaries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BeneficiaryResponse]:
    result = await db.execute(
        select(Beneficiary)
        .where(Beneficiary.user_id == current_user.id)
        .order_by(Beneficiary.last_used_at.desc().nullslast())
    )
    beneficiaries = result.scalars().all()
    return [BeneficiaryResponse.model_validate(b) for b in beneficiaries]


@router.post(
    "/me/beneficiaries",
    response_model=BeneficiaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a beneficiary",
)
async def add_beneficiary(
    body: BeneficiaryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BeneficiaryResponse:
    beneficiary = Beneficiary(
        user_id=current_user.id,
        display_name=body.display_name,
        masked_account=body.masked_account,
        trust_level="new",
    )
    db.add(beneficiary)

    audit_svc = AuditService(db)
    await audit_svc.log(
        event_type="beneficiary.created",
        actor_user_id=current_user.id,
        resource_type="beneficiary",
        metadata={"display_name": body.display_name},
    )

    await db.commit()
    await db.refresh(beneficiary)
    return BeneficiaryResponse.model_validate(beneficiary)
