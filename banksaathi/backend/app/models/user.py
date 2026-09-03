"""
User model.

Stores minimal user identity — no bank credentials, no Aadhaar.
Phone is hashed, never stored in plaintext.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    phone_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    # Prototype: hashed password for JWT-based auth
    # In production: use bank-provider authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    accessibility_profile: Mapped["AccessibilityProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    beneficiaries: Mapped[list["Beneficiary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    trusted_circle_members_as_user: Mapped[list["TrustedCircleMember"]] = relationship(
        "TrustedCircleMember",
        back_populates="user",
        foreign_keys="TrustedCircleMember.user_id",
        cascade="all, delete-orphan",
    )
