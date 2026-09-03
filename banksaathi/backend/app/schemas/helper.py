"""Helper schemas — abstracted view only, never expose secrets."""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HelperInvitationCreate(BaseModel):
    helper_phone: str = Field(..., min_length=10, max_length=15)


class HelperInvitationResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HelperSessionCreate(BaseModel):
    helper_user_id: uuid.UUID
    duration_minutes: int = Field(default=60, ge=5, le=480)


class HelperSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    helper_user_id: uuid.UUID
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class HelperAbstractedView(BaseModel):
    """
    What a helper can see during a guidance session.

    SECURITY GUARANTEE (SECURITY.md):
    - Shows intent, amount, beneficiary display name, risk level, guidance
    - NEVER includes: OTP, PIN, credentials, account numbers, full auth data
    """
    session_id: uuid.UUID
    current_step: str
    transaction_intent: str | None
    amount_display: str | None  # e.g. "₹5,000"
    beneficiary_display_name: str | None
    risk_level: str | None
    risk_reasons: list[str]
    suggested_guidance: str
    user_name: str
