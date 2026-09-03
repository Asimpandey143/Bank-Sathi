"""Beneficiary schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BeneficiaryCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    masked_account: str = Field(..., min_length=4, max_length=20)


class BeneficiaryResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    masked_account: str
    trust_level: str
    first_seen_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}
