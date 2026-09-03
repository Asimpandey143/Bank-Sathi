"""
AccessibilityProfile model.

Stores user's accessibility preferences.
Applied to the frontend on login.
Source: ACCESSIBILITY.md
"""
import uuid

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AccessibilityProfile(Base):
    __tablename__ = "accessibility_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    font_scale: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=1.0)
    high_contrast: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    screen_reader: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    speech_rate: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=1.0)
    # confirmation_mode: "single" | "double" | "voice"
    confirmation_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="single")
    # fraud_protection: "standard" | "high"
    fraud_protection: Mapped[str] = mapped_column(String(20), nullable=False, default="standard")

    user: Mapped["User"] = relationship(back_populates="accessibility_profile")
