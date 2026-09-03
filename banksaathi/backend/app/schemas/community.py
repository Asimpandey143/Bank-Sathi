"""Community session schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CommunitySessionCreate(BaseModel):
    topic: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(None, max_length=1000)
    scheduled_at: datetime
    max_participants: int = Field(default=50, ge=2, le=500)
    duration_minutes: int = Field(default=30, ge=10, le=120)


class CommunitySessionResponse(BaseModel):
    id: uuid.UUID
    host_id: uuid.UUID
    topic: str
    description: str | None
    scheduled_at: datetime
    status: str
    max_participants: int
    duration_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}
