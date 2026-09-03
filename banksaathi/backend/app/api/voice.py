"""
Voice & Accessibility API Routes

POST /api/v1/voice/synthesize-summary — Generate spoken summary and captions for a transaction.
"""
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.providers.voice import get_voice_provider
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/voice", tags=["Voice & Accessibility"])


class VoiceSummaryRequest(BaseModel):
    transaction_id: uuid.UUID


class VoiceSummaryResponse(BaseModel):
    speech_text: str
    caption_text: str
    language: str
    confirm_prompt: str
    cancel_prompt: str


@router.post(
    "/synthesize-summary",
    response_model=VoiceSummaryResponse,
    summary="Generate spoken narration and synchronous captions for accessibility",
)
async def synthesize_summary(
    body: VoiceSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VoiceSummaryResponse:
    tx_svc = TransactionService(db)
    tx = await tx_svc.get_transaction(body.transaction_id, current_user.id)

    voice_provider = get_voice_provider()
    reasons = None
    if tx.risk_reasons and "reasons" in tx.risk_reasons:
        reasons = tx.risk_reasons["reasons"]

    summary = voice_provider.generate_transaction_speech_summary(
        amount=tx.amount,
        currency=tx.currency,
        beneficiary_name=tx.beneficiary_name or "Recipient",
        risk_level=tx.risk_level or "LOW",
        risk_reasons=reasons,
    )
    return VoiceSummaryResponse(**summary)
