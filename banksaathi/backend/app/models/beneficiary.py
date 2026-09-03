"""
Beneficiary model.

Stores masked account info — never full account numbers.
trust_level drives risk engine scoring (new vs known).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Masked account — only last 4 digits, e.g. "****1234"
    masked_account: Mapped[str] = mapped_column(String(20), nullable=False)
    # "new" | "known" | "trusted"
    trust_level: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="beneficiaries")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="beneficiary")
