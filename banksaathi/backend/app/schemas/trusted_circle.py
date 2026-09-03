"""
Pydantic schemas for Trusted Circle & Second Opinion Model.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.trusted_circle import MemberStatus, NotificationStatus, SecondOpinionResponse


class InviteMemberRequest(BaseModel):
    phone: str = Field(..., description="Mobile number of the trusted family member or friend")
    relationship_label: str = Field(
        default="Family", description="Relationship label, e.g., Daughter, Son, Spouse, Parent"
    )


class TrustedCircleMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    trusted_person_id: uuid.UUID
    trusted_person_name: Optional[str] = None
    relationship_label: str
    status: str
    permissions: dict[str, Any]
    created_at: datetime
    verified_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SecondOpinionResponseDetail(BaseModel):
    id: uuid.UUID
    responder_id: uuid.UUID
    responder_name: Optional[str] = None
    response: str
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TrustedCircleNotificationResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    risk_level: str
    risk_reasons: dict[str, Any]
    amount_display: str
    beneficiary_display: str
    user_name: Optional[str] = None
    status: str
    created_at: datetime
    expires_at: datetime
    second_opinion: Optional[SecondOpinionResponseDetail] = None

    class Config:
        from_attributes = True


class SubmitSecondOpinionRequest(BaseModel):
    response: SecondOpinionResponse
    comment: Optional[str] = None


class SecondOpinionSummary(BaseModel):
    notification_id: Optional[uuid.UUID] = None
    has_notification: bool = False
    notification_status: Optional[str] = None
    response: Optional[str] = None
    responder_name: Optional[str] = None
    comment: Optional[str] = None
