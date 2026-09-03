"""
Transaction schemas.

SECURITY: Client CANNOT provide risk_score, risk_level, or status.
These are calculated server-side only.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class TransactionDraftCreate(BaseModel):
    """Create a transaction draft from parsed intent."""
    intent: Literal["TRANSFER", "PAY_BILL", "CHECK_BALANCE"] = "TRANSFER"
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="INR", max_length=3)
    beneficiary_id: uuid.UUID | None = None
    beneficiary_name: str | None = Field(None, max_length=255)
    raw_input: str | None = Field(None, max_length=500)


class RiskAssessRequest(BaseModel):
    """Optional context attributes for risk assessment (e.g. simulated device context)."""
    is_untrusted_device: bool = False
    is_unusual_time: bool = False


class TransactionConfirmRequest(BaseModel):
    """
    User-only final confirmation.

    The client sends only an explicit confirmation flag.
    The backend verifies: authenticated user + correct state + risk policy.
    """
    confirmed: bool = True


class RiskReasonResponse(BaseModel):
    reasons: list[str]
    score: int
    level: str


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    beneficiary_id: uuid.UUID | None
    beneficiary_name: str | None
    amount: Decimal
    currency: str
    intent: str
    status: str
    risk_score: int | None
    risk_level: str | None
    risk_reasons: dict | None
    bank_reference: str | None
    second_opinion: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
