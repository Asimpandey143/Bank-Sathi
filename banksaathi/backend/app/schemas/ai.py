"""
AI intent schemas.

LLM output is validated through Pydantic before any business logic.
Source: AI_ENGINE.md — "Never accept free-form LLM output for transaction execution"
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="User's natural language input")


class IntentResponse(BaseModel):
    """
    Structured intent extracted from natural language.

    SECURITY: This is validated by Pydantic before being used to create
    a transaction draft. The LLM output NEVER directly executes anything.
    """
    intent: Literal[
        "CHECK_BALANCE",
        "TRANSFER",
        "PAY_BILL",
        "LIST_TRANSACTIONS",
        "HELP",
        "CANCEL",
        "UNKNOWN",
    ]
    amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="INR", max_length=3)
    beneficiary_name: str | None = Field(None, max_length=255)
    confidence: float = Field(..., ge=0.0, le=1.0)
    clarification_needed: bool = False
    clarification_question: str | None = None
