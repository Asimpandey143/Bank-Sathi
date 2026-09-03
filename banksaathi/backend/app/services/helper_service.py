"""
Helper Service

Implements the core BankSathi safety principle:
"Shared guidance, not shared access."

SECURITY RULES (AGENTS.md, SECURITY.md):
- Helper can GUIDE, never CONTROL
- Helper CANNOT approve, execute, or modify transactions
- Helper NEVER receives OTP, PIN, password, credentials
- Helper sessions are strictly time-limited and expire automatically
- All helper actions generate audit events
"""
from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_phone
from app.core.errors import (
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.models.helper_assignment import AssignmentStatus, HelperAssignment
from app.models.helper_session import HelperSession, SessionStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.user import User
from app.schemas.helper import HelperAbstractedView
from app.services.audit_service import AuditService


class HelperService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit_service = AuditService(db)

    async def create_invitation(
        self, user_id: uuid.UUID, helper_phone: str
    ) -> HelperAssignment:
        """Create an invitation for a trusted helper by phone number."""
        phone_hash = hash_phone(helper_phone)
        helper_stmt = select(User).where(User.phone_hash == phone_hash)
        helper_res = await self.db.execute(helper_stmt)
        helper_user = helper_res.scalar_one_or_none()

        if not helper_user:
            # Create a pending helper user record for prototype
            from app.core.auth import hash_password
            helper_user = User(
                phone_hash=phone_hash,
                name=f"Helper ({helper_phone[-4:]})",
                hashed_password=hash_password("helperpass123"),
                role="helper",
            )
            self.db.add(helper_user)
            await self.db.flush()

        if helper_user.id == user_id:
            raise ForbiddenError("You cannot invite yourself as a helper.")

        assignment = HelperAssignment(
            user_id=user_id,
            helper_user_id=helper_user.id,
            status=AssignmentStatus.PENDING,
        )
        self.db.add(assignment)

        await self.audit_service.log(
            event_type="helper.invitation_created",
            actor_user_id=user_id,
            resource_type="helper_assignment",
            resource_id=assignment.id,
        )
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def accept_invitation(
        self, assignment_id: uuid.UUID, helper_user_id: uuid.UUID
    ) -> HelperAssignment:
        """Helper accepts the invitation."""
        stmt = select(HelperAssignment).where(
            HelperAssignment.id == assignment_id,
            HelperAssignment.helper_user_id == helper_user_id,
        )
        res = await self.db.execute(stmt)
        assignment = res.scalar_one_or_none()
        if not assignment:
            raise NotFoundError("Helper invitation")

        assignment.status = AssignmentStatus.ACTIVE

        await self.audit_service.log(
            event_type="helper.invitation_accepted",
            actor_user_id=helper_user_id,
            resource_type="helper_assignment",
            resource_id=assignment.id,
        )
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def create_session(
        self, user_id: uuid.UUID, helper_user_id: uuid.UUID, duration_minutes: int = 60
    ) -> HelperSession:
        """Create a temporary, time-limited helper session."""
        # Verify assignment is active
        stmt = select(HelperAssignment).where(
            HelperAssignment.user_id == user_id,
            HelperAssignment.helper_user_id == helper_user_id,
            HelperAssignment.status == AssignmentStatus.ACTIVE,
        )
        res = await self.db.execute(stmt)
        assignment = res.scalar_one_or_none()
        if not assignment:
            raise ForbiddenError("No active helper assignment exists with this user.")

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=duration_minutes)

        session = HelperSession(
            user_id=user_id,
            helper_user_id=helper_user_id,
            status=SessionStatus.ACTIVE,
            expires_at=expires_at,
        )
        self.db.add(session)

        await self.audit_service.log(
            event_type="helper.session_created",
            actor_user_id=user_id,
            resource_type="helper_session",
            resource_id=session.id,
            metadata={"expires_at": expires_at.isoformat()},
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_abstracted_view(
        self, session_id: uuid.UUID, helper_user_id: uuid.UUID
    ) -> HelperAbstractedView:
        """
        Produce safe, abstracted guidance view for the helper.

        SECURITY GUARANTEE:
        - NEVER returns OTP, PIN, password, banking credentials
        - Helper sees only: step, intent, amount, recipient name, risk, suggested guidance
        """
        stmt = select(HelperSession).where(
            HelperSession.id == session_id,
            HelperSession.helper_user_id == helper_user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise NotFoundError("Helper session")

        now = datetime.now(timezone.utc)
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Check automatic expiration
        if now > expires_at:
            session.status = SessionStatus.EXPIRED
            await self.db.commit()
            raise ForbiddenError("This helper session has expired.")

        if session.status != SessionStatus.ACTIVE:
            raise ForbiddenError(f"Helper session is currently {session.status}.")

        # Get user
        user_stmt = select(User).where(User.id == session.user_id)
        user_res = await self.db.execute(user_stmt)
        user = user_res.scalar_one()

        # Get latest active transaction for the user
        tx_stmt = (
            select(Transaction)
            .where(
                Transaction.user_id == session.user_id,
                Transaction.status.in_([
                    TransactionStatus.PARSED,
                    TransactionStatus.RISK_ASSESSED,
                    TransactionStatus.AWAITING_CONFIRMATION,
                    TransactionStatus.BLOCKED,
                ]),
            )
            .order_by(Transaction.created_at.desc())
        )
        tx_res = await self.db.execute(tx_stmt)
        latest_tx = tx_res.scalars().first()

        # Build abstracted guidance
        current_step = "Dashboard"
        transaction_intent = None
        amount_display = None
        beneficiary_name = None
        risk_level = None
        risk_reasons: list[str] = []
        guidance = "User is on dashboard. Ready to provide assistance."

        if latest_tx:
            current_step = f"Reviewing Transaction ({latest_tx.status})"
            transaction_intent = latest_tx.intent
            amount_display = f"₹{latest_tx.amount:,.2f}"
            beneficiary_name = latest_tx.beneficiary_name or "Recipient"
            risk_level = latest_tx.risk_level

            if latest_tx.risk_reasons and "reasons" in latest_tx.risk_reasons:
                risk_reasons = latest_tx.risk_reasons["reasons"]

            if latest_tx.risk_level == "CRITICAL":
                guidance = "This transaction has been blocked for user safety. Please explain the safety risk to the user."
            elif latest_tx.risk_level in ("HIGH", "MEDIUM"):
                guidance = "Please ask the user to verify the amount and recipient before they confirm on their device."
            else:
                guidance = "Transaction parameters appear normal. Guide the user to confirm if they wish to proceed."

        await self.audit_service.log(
            event_type="helper.view_accessed",
            actor_user_id=helper_user_id,
            resource_type="helper_session",
            resource_id=session_id,
        )
        await self.db.commit()

        return HelperAbstractedView(
            session_id=session_id,
            current_step=current_step,
            transaction_intent=transaction_intent,
            amount_display=amount_display,
            beneficiary_display_name=beneficiary_name,
            risk_level=risk_level,
            risk_reasons=risk_reasons,
            suggested_guidance=guidance,
            user_name=user.name,
        )

    async def pause_session(
        self, session_id: uuid.UUID, actor_user_id: uuid.UUID
    ) -> HelperSession:
        stmt = select(HelperSession).where(
            HelperSession.id == session_id,
            (HelperSession.user_id == actor_user_id) | (HelperSession.helper_user_id == actor_user_id),
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise NotFoundError("Helper session")

        session.status = SessionStatus.PAUSED
        await self.audit_service.log(
            event_type="helper.session_paused",
            actor_user_id=actor_user_id,
            resource_type="helper_session",
            resource_id=session.id,
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session
