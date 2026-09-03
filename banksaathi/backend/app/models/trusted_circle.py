"""
Trusted Circle Database Models

Implements the Trusted Circle & Risk-Based Verification architecture:
- TrustedCircleMember: Family/trusted person with explicit relationship & granular permissions
- TrustedCircleNotification: Privacy-safe risk notification with no secrets
- TrustedCircleResponse: Advisory second opinion (LOOKS_EXPECTED, NOT_RECOGNIZED, REQUEST_USER_VERIFICATION)
"""
import uuid
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MemberStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    RESPONDED = "responded"
    EXPIRED = "expired"


class SecondOpinionResponse(StrEnum):
    LOOKS_EXPECTED = "LOOKS_EXPECTED"
    NOT_RECOGNIZED = "NOT_RECOGNIZED"
    REQUEST_USER_VERIFICATION = "REQUEST_USER_VERIFICATION"


DEFAULT_TRUSTED_CIRCLE_PERMISSIONS = {
    "receive_risk_notifications": True,
    "view_transaction_summary": True,
    "provide_second_opinion": True,
    "contact_user": True,
    "execute_transaction": False,
    "approve_transaction": False,
    "modify_transaction": False,
    "view_credentials": False,
    "view_otp": False,
    "view_upi_pin": False,
    "remote_control": False,
    "screen_share": False,
}


class TrustedCircleMember(Base):
    __tablename__ = "trusted_circle_members"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trusted_person_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relationship_label: Mapped[str] = mapped_column(String(50), nullable=False, default="Family")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MemberStatus.PENDING
    )
    permissions: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=lambda: dict(DEFAULT_TRUSTED_CIRCLE_PERMISSIONS)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="trusted_circle_members_as_user"
    )
    trusted_person: Mapped["User"] = relationship(
        "User", foreign_keys=[trusted_person_id]
    )
    notifications: Mapped[list["TrustedCircleNotification"]] = relationship(
        "TrustedCircleNotification", back_populates="member", cascade="all, delete-orphan"
    )


class TrustedCircleNotification(Base):
    __tablename__ = "trusted_circle_notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trusted_circle_member_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trusted_circle_members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_reasons: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    amount_display: Mapped[str] = mapped_column(String(50), nullable=False)
    beneficiary_display: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    member: Mapped["TrustedCircleMember"] = relationship(
        "TrustedCircleMember", back_populates="notifications"
    )
    transaction: Mapped["Transaction"] = relationship("Transaction")
    response: Mapped["TrustedCircleResponse | None"] = relationship(
        "TrustedCircleResponse", uselist=False, back_populates="notification"
    )


class TrustedCircleResponse(Base):
    __tablename__ = "trusted_circle_responses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    notification_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trusted_circle_notifications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    responder_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    response: Mapped[str] = mapped_column(String(50), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    notification: Mapped["TrustedCircleNotification"] = relationship(
        "TrustedCircleNotification", back_populates="response"
    )
    responder: Mapped["User"] = relationship("User")
