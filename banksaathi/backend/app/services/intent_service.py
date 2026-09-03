"""
AI Intent Service

Coordinates natural language understanding through LLMProvider.
Validates all outputs against Pydantic schemas.

CRITICAL PRINCIPLE (AI_ENGINE.md, SECURITY.md):
- AI assists understanding; deterministic backend code controls money movement.
- LLM output is untrusted input.
- IntentService NEVER directly executes transactions or invokes the banking provider.
"""
from app.providers.llm import LLMProvider, get_llm_provider
from app.schemas.ai import IntentResponse


class IntentService:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    async def parse(self, text: str) -> IntentResponse:
        """
        Parse natural language into structured banking intent.
        Output is validated by Pydantic IntentResponse model.
        """
        response = await self.provider.parse_intent(text)
        # Ensure Pydantic model validation
        return IntentResponse.model_validate(response)
