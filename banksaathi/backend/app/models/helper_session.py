"""
HelperSession model.

Temporary, time-limited session during which a helper can guide a user.
Expires automatically — a helper cannot maintain indefinite access.
Source: SECURITY.md — temporary sessions, least privilege
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import StrEnum

from app.database import Base


class SessionStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    EXPIRED = "expired"


class HelperSession(Base):
    __tablename__ = "helper_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    helper_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SessionStatus.ACTIVE
    )
    # Session expires_at — backend enforces expiry
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="helper_sessions_as_user", foreign_keys=[user_id]
    )
    helper: Mapped["User"] = relationship(foreign_keys=[helper_user_id])
