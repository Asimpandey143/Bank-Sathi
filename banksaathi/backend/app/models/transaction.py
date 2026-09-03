"""
Transaction model + state machine status enum.

CRITICAL RULES (from ARCHITECTURE.md + SECURITY.md):
- Backend validates ALL state transitions
- Frontend cannot set risk_score, risk_level, or status
- ONLY the authenticated user can move to CONFIRMED
- Idempotency key prevents duplicate transactions

State machine:
    DRAFT → PARSED → RISK_ASSESSED → AWAITING_CONFIRMATION → CONFIRMED → PROCESSING → COMPLETED
                                  ↘ BLOCKED
                                                          ↘ CANCELLED
                                                                                    ↘ FAILED
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TransactionStatus(StrEnum):
    DRAFT = "DRAFT"
    PARSED = "PARSED"
    RISK_ASSESSED = "RISK_ASSESSED"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


# Valid transitions: maps current status → set of allowed next statuses
VALID_TRANSITIONS: dict[TransactionStatus, set[TransactionStatus]] = {
    TransactionStatus.DRAFT: {TransactionStatus.PARSED, TransactionStatus.CANCELLED},
    TransactionStatus.PARSED: {TransactionStatus.RISK_ASSESSED, TransactionStatus.CANCELLED},
    TransactionStatus.RISK_ASSESSED: {
        TransactionStatus.AWAITING_CONFIRMATION,
        TransactionStatus.BLOCKED,
        TransactionStatus.CANCELLED,
    },
    TransactionStatus.AWAITING_CONFIRMATION: {
        TransactionStatus.CONFIRMED,
        TransactionStatus.CANCELLED,
    },
    TransactionStatus.CONFIRMED: {TransactionStatus.PROCESSING},
    TransactionStatus.PROCESSING: {
        TransactionStatus.COMPLETED,
        TransactionStatus.FAILED,
    },
    # Terminal states — no further transitions
    TransactionStatus.COMPLETED: set(),
    TransactionStatus.CANCELLED: set(),
    TransactionStatus.BLOCKED: set(),
    TransactionStatus.FAILED: set(),
}


def is_valid_transition(from_status: TransactionStatus, to_status: TransactionStatus) -> bool:
    """Returns True if the state transition is valid per the state machine."""
    return to_status in VALID_TRANSITIONS.get(from_status, set())


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    beneficiary_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    intent: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=TransactionStatus.DRAFT
    )
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # JSONB stores list of human-readable risk reason strings
    risk_reasons: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Idempotency key — prevents duplicate bank submissions
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    # Bank reference returned by MockBankingProvider
    bank_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Raw NL input that was parsed into this transaction
    raw_input: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Beneficiary display name (cached — beneficiary may be new, not yet in DB)
    beneficiary_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
    beneficiary: Mapped["Beneficiary | None"] = relationship(back_populates="transactions")
