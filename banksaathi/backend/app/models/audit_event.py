"""
AuditEvent model.

Immutable security audit log.

SECURITY RULE: Never log OTP, PIN, passwords, credentials.
Logs safe fields only: event type, resource, user ID, metadata.
Source: SECURITY.md
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # actor_user_id can be NULL for system events
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    # Safe metadata only — never store secrets here
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
