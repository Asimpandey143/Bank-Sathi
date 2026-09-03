"""
Trusted Circle API Router

Endpoints:
- POST   /api/v1/trusted-circle/members/invite
- GET    /api/v1/trusted-circle/members
- DELETE /api/v1/trusted-circle/members/{id}
- GET    /api/v1/trusted-circle/notifications
- GET    /api/v1/trusted-circle/notifications/{id}
- POST   /api/v1/trusted-circle/notifications/{id}/response
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.trusted_circle import (
    InviteMemberRequest,
    SecondOpinionResponseDetail,
    SubmitSecondOpinionRequest,
    TrustedCircleMemberResponse,
    TrustedCircleNotificationResponse,
)
from app.services.trusted_circle_service import TrustedCircleService

router = APIRouter(prefix="/trusted-circle", tags=["trusted-circle"])


@router.post(
    "/members/invite",
    response_model=TrustedCircleMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a trusted family member or friend to your Trusted Circle",
)
async def invite_member(
    payload: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrustedCircleService(db)
    member = await service.invite_member(
        current_user, payload.phone, payload.relationship_label
    )
    return TrustedCircleMemberResponse(
        id=member.id,
        user_id=member.user_id,
        trusted_person_id=member.trusted_person_id,
        trusted_person_name=member.trusted_person.name if member.trusted_person else None,
        relationship_label=member.relationship_label,
        status=member.status,
        permissions=member.permissions,
        created_at=member.created_at,
        verified_at=member.verified_at,
    )


@router.get(
    "/members",
    response_model=List[TrustedCircleMemberResponse],
    summary="List all trusted circle members for the current user",
)
async def list_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrustedCircleService(db)
    members = await service.list_members(current_user.id)
    return [
        TrustedCircleMemberResponse(
            id=m.id,
            user_id=m.user_id,
            trusted_person_id=m.trusted_person_id,
            trusted_person_name=m.trusted_person.name if m.trusted_person else None,
            relationship_label=m.relationship_label,
            status=m.status,
            permissions=m.permissions,
            created_at=m.created_at,
            verified_at=m.verified_at,
        )
        for m in members
    ]


@router.delete(
    "/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a member from your Trusted Circle",
)
async def revoke_member(
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrustedCircleService(db)
    await service.revoke_member(current_user.id, member_id)


@router.get(
    "/notifications",
    response_model=List[TrustedCircleNotificationResponse],
    summary="List risk notifications received by the trusted circle member",
)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrustedCircleService(db)
    notifications = await service.list_notifications_for_trusted_person(current_user.id)
    res = []
    for n in notifications:
        second_opinion = None
        if n.response:
            second_opinion = SecondOpinionResponseDetail(
                id=n.response.id,
                responder_id=n.response.responder_id,
                responder_name=n.response.responder.name if n.response.responder else None,
                response=n.response.response,
                comment=n.response.comment,
                created_at=n.response.created_at,
            )
        res.append(
            TrustedCircleNotificationResponse(
                id=n.id,
                transaction_id=n.transaction_id,
                risk_level=n.risk_level,
                risk_reasons=n.risk_reasons,
                amount_display=n.amount_display,
                beneficiary_display=n.beneficiary_display,
                user_name=n.member.user.name if n.member and n.member.user else None,
                status=n.status,
                created_at=n.created_at,
                expires_at=n.expires_at,
                second_opinion=second_opinion,
            )
        )
    return res


@router.get(
    "/notifications/{notification_id}",
    response_model=TrustedCircleNotificationResponse,
    summary="Get privacy-safe transaction risk details for a notification",
)
async def get_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrustedCircleService(db)
    n = await service.get_notification_detail(notification_id, current_user.id)
    second_opinion = None
    if n.response:
        second_opinion = SecondOpinionResponseDetail(
            id=n.response.id,
            responder_id=n.response.responder_id,
            responder_name=n.response.responder.name if n.response.responder else None,
            response=n.response.response,
            comment=n.response.comment,
            created_at=n.response.created_at,
        )
    return TrustedCircleNotificationResponse(
        id=n.id,
        transaction_id=n.transaction_id,
        risk_level=n.risk_level,
        risk_reasons=n.risk_reasons,
        amount_display=n.amount_display,
        beneficiary_display=n.beneficiary_display,
        user_name=n.member.user.name if n.member and n.member.user else None,
        status=n.status,
        created_at=n.created_at,
        expires_at=n.expires_at,
        second_opinion=second_opinion,
    )


@router.post(
    "/notifications/{notification_id}/response",
    response_model=SecondOpinionResponseDetail,
    summary="Submit advisory second opinion (LOOKS_EXPECTED, NOT_RECOGNIZED, REQUEST_USER_VERIFICATION)",
)
async def submit_response(
    notification_id: uuid.UUID,
    payload: SubmitSecondOpinionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrustedCircleService(db)
    opinion = await service.submit_second_opinion(
        notification_id=notification_id,
        responder=current_user,
        response_type=payload.response,
        comment=payload.comment,
    )
    return SecondOpinionResponseDetail(
        id=opinion.id,
        responder_id=opinion.responder_id,
        responder_name=current_user.name,
        response=opinion.response,
        comment=opinion.comment,
        created_at=opinion.created_at,
    )
