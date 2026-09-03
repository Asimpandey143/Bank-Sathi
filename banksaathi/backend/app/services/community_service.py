"""
Community Session Service

Supports group digital banking literacy sessions (WORKFLOWS.md - Workflow E).

CRITICAL PRIVACY RULE (SECURITY.md):
- Community sessions are for learning and literacy ONLY.
- They MUST NOT expose any user's personal banking data, balance, transaction history,
  OTP, PIN, or credentials to any participant.
"""
from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.community_session import CommunitySession, CommunitySessionStatus
from app.services.audit_service import AuditService


class CommunityService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit_service = AuditService(db)

    async def list_sessions(
        self, limit: int = 20, offset: int = 0
    ) -> list[CommunitySession]:
        stmt = (
            select(CommunitySession)
            .where(
                CommunitySession.status.in_([
                    CommunitySessionStatus.SCHEDULED,
                    CommunitySessionStatus.LIVE,
                ])
            )
            .order_by(CommunitySession.scheduled_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_session(self, session_id: uuid.UUID) -> CommunitySession:
        stmt = select(CommunitySession).where(CommunitySession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError("Community session")
        return session

    async def create_session(
        self,
        host_id: uuid.UUID,
        topic: str,
        description: str | None,
        scheduled_at: datetime,
        max_participants: int = 50,
        duration_minutes: int = 30,
    ) -> CommunitySession:
        session = CommunitySession(
            host_id=host_id,
            topic=topic,
            description=description,
            scheduled_at=scheduled_at,
            max_participants=max_participants,
            duration_minutes=duration_minutes,
            status=CommunitySessionStatus.SCHEDULED,
        )
        self.db.add(session)

        await self.audit_service.log(
            event_type="community.session_created",
            actor_user_id=host_id,
            resource_type="community_session",
            resource_id=session.id,
            metadata={"topic": topic, "scheduled_at": scheduled_at.isoformat()},
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def join_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> dict:
        session = await self.get_session(session_id)
        if session.status in (CommunitySessionStatus.COMPLETED, CommunitySessionStatus.CANCELLED):
            raise ValidationError("This session is no longer active.")

        await self.audit_service.log(
            event_type="community.session_joined",
            actor_user_id=user_id,
            resource_type="community_session",
            resource_id=session_id,
        )
        await self.db.commit()

        return {
            "session_id": session.id,
            "topic": session.topic,
            "status": session.status,
            "message": "Joined community learning session. Privacy protection active: No banking data shared.",
        }
