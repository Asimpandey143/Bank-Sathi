"""Audit event schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: uuid.UUID
    actor_user_id: uuid.UUID | None
    event_type: str
    resource_type: str | None
    resource_id: uuid.UUID | None
    metadata_: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
