"""
Trusted Circle Service

Implements the business logic for:
- Inviting and verifying trusted circle members (daughter, son, spouse, etc.)
- Revoking trusted members
- Generating privacy-safe risk notifications (for MEDIUM / HIGH / CRITICAL transactions)
- Recording advisory second opinions (LOOKS_EXPECTED, NOT_RECOGNIZED, REQUEST_USER_VERIFICATION)
- Strict security enforcement: Second opinions CANNOT approve or execute payments!
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import hash_password, hash_phone
from app.core.errors import ForbiddenError, NotFoundError, ValidationError
from app.models.audit_event import AuditEvent
from app.models.transaction import Transaction
from app.models.trusted_circle import (
    MemberStatus,
    NotificationStatus,
    SecondOpinionResponse,
    TrustedCircleMember,
    TrustedCircleNotification,
    TrustedCircleResponse,
)
from app.models.user import User


class TrustedCircleService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def invite_member(
        self, user: User, phone: str, relationship_label: str = "Family"
    ) -> TrustedCircleMember:
        """Invite a trusted person by mobile number."""
        clean_phone = phone.strip().replace(" ", "").replace("-", "")
        if len(clean_phone) < 10:
            raise ValidationError("Valid 10-digit mobile number required.")

        phone_hash = hash_phone(clean_phone)

        # Look up or create trusted person user account
        res = await self.session.execute(select(User).where(User.phone_hash == phone_hash))
        trusted_person = res.scalar_one_or_none()

        if not trusted_person:
            trusted_person = User(
                name=f"{relationship_label} ({clean_phone[-4:]})",
                phone_hash=phone_hash,
                hashed_password=hash_password("trustedSecret123!"),
                role="helper",
            )
            self.session.add(trusted_person)
            await self.session.flush()

        if trusted_person.id == user.id:
            raise ValidationError("You cannot add yourself to your Trusted Circle.")

        # Check existing membership
        existing_res = await self.session.execute(
            select(TrustedCircleMember).where(
                TrustedCircleMember.user_id == user.id,
                TrustedCircleMember.trusted_person_id == trusted_person.id,
            )
        )
        existing = existing_res.scalar_one_or_none()
        if existing:
            if existing.status == MemberStatus.REVOKED:
                existing.status = MemberStatus.ACTIVE
                existing.relationship_label = relationship_label
                existing.verified_at = datetime.now(timezone.utc)
                existing.revoked_at = None
                await self.session.commit()
                return existing
            return existing

        member = TrustedCircleMember(
            user_id=user.id,
            trusted_person_id=trusted_person.id,
            relationship_label=relationship_label,
            status=MemberStatus.ACTIVE,  # Active for demo/verified contact
            verified_at=datetime.now(timezone.utc),
        )
        self.session.add(member)

        audit = AuditEvent(
            actor_user_id=user.id,
            event_type="TRUSTED_CIRCLE_MEMBER_INVITED",
            resource_type="trusted_circle_member",
            resource_id=member.id,
            metadata_={"relationship": relationship_label},
        )
        self.session.add(audit)
        await self.session.commit()

        # Eagerly reload with trusted_person relationship
        reloaded = await self.session.execute(
            select(TrustedCircleMember)
            .options(selectinload(TrustedCircleMember.trusted_person))
            .where(TrustedCircleMember.id == member.id)
        )
        return reloaded.scalar_one()

    async def list_members(self, user_id: uuid.UUID) -> List[TrustedCircleMember]:
        """List active/pending trusted circle members for a user."""
        res = await self.session.execute(
            select(TrustedCircleMember)
            .options(selectinload(TrustedCircleMember.trusted_person))
            .where(
                TrustedCircleMember.user_id == user_id,
                TrustedCircleMember.status != MemberStatus.REVOKED,
            )
            .order_by(TrustedCircleMember.created_at.desc())
        )
        return list(res.scalars().all())

    async def revoke_member(self, user_id: uuid.UUID, member_id: uuid.UUID):
        """Revoke trusted circle member access."""
        res = await self.session.execute(
            select(TrustedCircleMember).where(
                TrustedCircleMember.id == member_id,
                TrustedCircleMember.user_id == user_id,
            )
        )
        member = res.scalar_one_or_none()
        if not member:
            raise NotFoundError("Trusted circle member not found.")

        member.status = MemberStatus.REVOKED
        member.revoked_at = datetime.now(timezone.utc)

        audit = AuditEvent(
            actor_user_id=user_id,
            event_type="TRUSTED_CIRCLE_MEMBER_REVOKED",
            resource_type="trusted_circle_member",
            resource_id=member.id,
        )
        self.session.add(audit)
        await self.session.commit()

    async def generate_notifications_if_needed(
        self, tx: Transaction
    ) -> List[TrustedCircleNotification]:
        """Generate privacy-safe notifications for active trusted members if risk is MEDIUM, HIGH, or CRITICAL."""
        if tx.risk_level not in ("MEDIUM", "HIGH", "CRITICAL"):
            return []

        # Find active members
        members_res = await self.session.execute(
            select(TrustedCircleMember).where(
                TrustedCircleMember.user_id == tx.user_id,
                TrustedCircleMember.status == MemberStatus.ACTIVE,
            )
        )
        members = members_res.scalars().all()
        if not members:
            return []

        amount_str = f"₹{float(tx.amount):,.2f}"
        beneficiary_str = tx.beneficiary_name or "Recipient"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

        created_notifications = []
        for m in members:
            notification = TrustedCircleNotification(
                transaction_id=tx.id,
                trusted_circle_member_id=m.id,
                risk_level=tx.risk_level,
                risk_reasons=tx.risk_reasons or {},
                amount_display=amount_str,
                beneficiary_display=beneficiary_str,
                status=NotificationStatus.PENDING,
                expires_at=expires_at,
            )
            self.session.add(notification)
            created_notifications.append(notification)

            audit = AuditEvent(
                actor_user_id=tx.user_id,
                event_type="TRUSTED_CIRCLE_NOTIFICATION_GENERATED",
                resource_type="trusted_circle_notification",
                resource_id=notification.id,
                metadata_={
                    "risk_level": tx.risk_level,
                    "trusted_person_id": str(m.trusted_person_id),
                },
            )
            self.session.add(audit)

        await self.session.commit()
        return created_notifications

    async def list_notifications_for_trusted_person(
        self, trusted_person_id: uuid.UUID
    ) -> List[TrustedCircleNotification]:
        """List notifications sent to a trusted person where member is not revoked."""
        res = await self.session.execute(
            select(TrustedCircleNotification)
            .join(TrustedCircleMember)
            .options(
                selectinload(TrustedCircleNotification.member).selectinload(
                    TrustedCircleMember.user
                ),
                selectinload(TrustedCircleNotification.response).selectinload(
                    TrustedCircleResponse.responder
                ),
            )
            .where(
                TrustedCircleMember.trusted_person_id == trusted_person_id,
                TrustedCircleMember.status == MemberStatus.ACTIVE,
            )
            .order_by(TrustedCircleNotification.created_at.desc())
        )
        return list(res.scalars().all())

    async def get_notification_detail(
        self, notification_id: uuid.UUID, trusted_person_id: uuid.UUID
    ) -> TrustedCircleNotification:
        """Get notification detail, ensuring caller is the authorized trusted person."""
        res = await self.session.execute(
            select(TrustedCircleNotification)
            .join(TrustedCircleMember)
            .options(
                selectinload(TrustedCircleNotification.member).selectinload(
                    TrustedCircleMember.user
                ),
                selectinload(TrustedCircleNotification.response).selectinload(
                    TrustedCircleResponse.responder
                ),
            )
            .where(
                TrustedCircleNotification.id == notification_id,
                TrustedCircleMember.trusted_person_id == trusted_person_id,
                TrustedCircleMember.status == MemberStatus.ACTIVE,
            )
        )
        notification = res.scalar_one_or_none()
        if not notification:
            raise NotFoundError("Notification not found or access denied.")
        return notification

    async def submit_second_opinion(
        self,
        notification_id: uuid.UUID,
        responder: User,
        response_type: SecondOpinionResponse,
        comment: Optional[str] = None,
    ) -> TrustedCircleResponse:
        """
        Submit advisory second opinion.
        CRITICAL SAFETY: This records an advisory signal ONLY. It CANNOT approve or execute payments!
        """
        notification = await self.get_notification_detail(notification_id, responder.id)

        # Check if already responded
        if notification.status == NotificationStatus.RESPONDED:
            raise ValidationError("A second opinion has already been submitted for this notification.")

        # Check expiration
        now = datetime.now(timezone.utc)
        exp = notification.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < now:
            notification.status = NotificationStatus.EXPIRED
            await self.session.commit()
            raise ValidationError("This notification has expired.")

        opinion = TrustedCircleResponse(
            notification_id=notification.id,
            responder_id=responder.id,
            response=response_type.value,
            comment=comment,
        )
        self.session.add(opinion)
        notification.status = NotificationStatus.RESPONDED

        audit = AuditEvent(
            actor_user_id=responder.id,
            event_type="TRUSTED_CIRCLE_SECOND_OPINION_SUBMITTED",
            resource_type="trusted_circle_response",
            resource_id=opinion.id,
            metadata_={
                "response": response_type.value,
                "transaction_id": str(notification.transaction_id),
            },
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(opinion)
        return opinion

    async def get_second_opinion_for_transaction(
        self, tx_id: uuid.UUID
    ) -> dict:
        """Fetch latest second opinion advisory signal for user transaction review screen."""
        res = await self.session.execute(
            select(TrustedCircleNotification)
            .options(
                selectinload(TrustedCircleNotification.response).selectinload(
                    TrustedCircleResponse.responder
                ),
                selectinload(TrustedCircleNotification.member),
            )
            .where(TrustedCircleNotification.transaction_id == tx_id)
            .order_by(TrustedCircleNotification.created_at.desc())
        )
        notification = res.scalar_one_or_none()
        if not notification:
            return {"has_notification": False}

        summary = {
            "has_notification": True,
            "notification_id": str(notification.id),
            "notification_status": notification.status,
            "risk_level": notification.risk_level,
            "relationship_label": notification.member.relationship_label if notification.member else "Trusted Contact",
        }

        if notification.response:
            summary.update({
                "response": notification.response.response,
                "responder_name": notification.response.responder.name if notification.response.responder else "Trusted Person",
                "comment": notification.response.comment,
            })

        return summary
