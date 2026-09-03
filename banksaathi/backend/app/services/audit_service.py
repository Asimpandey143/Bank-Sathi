"""
Audit event service.

Writes immutable security audit events.

SECURITY RULE: Never log OTP, PIN, password, credentials in metadata.
Only log safe fields: event type, resource IDs, risk levels, statuses.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log(
        self,
        event_type: str,
        actor_user_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:
        """
        Write an immutable audit event.

        NEVER include in metadata:
        - OTP values
        - PIN values
        - plaintext passwords
        - raw bank credentials
        """
        event = AuditEvent(
            actor_user_id=actor_user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_=metadata,
        )
        self._db.add(event)
        # Don't commit here — let the calling service commit atomically
        return event
