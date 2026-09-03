"""User and auth schemas."""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserRegisterRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, description="Prototype password — not stored plaintext")


class UserLoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AccessibilityPreferencesUpdate(BaseModel):
    language: str | None = Field(None, max_length=10)
    font_scale: float | None = Field(None, ge=0.5, le=3.0)
    high_contrast: bool | None = None
    screen_reader: bool | None = None
    speech_rate: float | None = Field(None, ge=0.25, le=4.0)
    confirmation_mode: Literal["single", "double", "voice"] | None = None
    fraud_protection: Literal["standard", "high"] | None = None


class AccessibilityProfileResponse(BaseModel):
    user_id: uuid.UUID
    language: str
    font_scale: float
    high_contrast: bool
    screen_reader: bool
    speech_rate: float
    confirmation_mode: str
    fraud_protection: str

    model_config = {"from_attributes": True}
