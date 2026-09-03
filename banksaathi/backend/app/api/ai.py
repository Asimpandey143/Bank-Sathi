"""
AI API Routes

POST /api/v1/ai/parse-intent — Natural language understanding for banking actions.

SAFETY RULE:
This endpoint only returns structured intent JSON.
It does NOT create or execute transactions.
The frontend or client must use the returned intent to explicitly request
transaction draft creation via /transactions/draft.
"""
from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.ai import IntentRequest, IntentResponse
from app.services.intent_service import IntentService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/parse-intent",
    response_model=IntentResponse,
    summary="Parse natural language banking command",
)
async def parse_intent(
    body: IntentRequest,
    current_user: User = Depends(get_current_user),
) -> IntentResponse:
    """
    Convert conversational voice/text input into structured intent.
    Output is strictly validated against Pydantic schema.
    """
    svc = IntentService()
    return await svc.parse(body.text)
