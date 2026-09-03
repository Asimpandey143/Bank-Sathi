"""
Phase 6 tests — Voice & Accessibility Backend

Tests:
- Spoken narration generation for low, medium, and critical transactions
- Caption text generation for synchronous visual display
- Clear language and non-jargon explanations
- API endpoint: POST /api/v1/voice/synthesize-summary
"""
from decimal import Decimal
import pytest
from httpx import AsyncClient

from app.providers.voice import MockVoiceProvider

USER1 = {
    "phone": "9999999501",
    "name": "Meena Devi",
    "password": "password123",
}


async def register_and_login(client: AsyncClient, user_data: dict) -> str:
    await client.post("/api/v1/auth/register", json=user_data)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": user_data["phone"], "password": user_data["password"]},
    )
    return resp.json()["access_token"]


def test_voice_summary_generation_low_risk():
    provider = MockVoiceProvider()
    summary = provider.generate_transaction_speech_summary(
        amount=Decimal("1000.00"),
        currency="INR",
        beneficiary_name="Ravi Kumar",
        risk_level="LOW",
    )
    assert "1,000.00 rupees to Ravi Kumar" in summary["speech_text"]
    assert "Everything looks normal" in summary["speech_text"]
    assert "₹1,000.00" in summary["caption_text"]


def test_voice_summary_generation_medium_risk():
    provider = MockVoiceProvider()
    summary = provider.generate_transaction_speech_summary(
        amount=Decimal("5000.00"),
        currency="INR",
        beneficiary_name="Ravi Kumar",
        risk_level="MEDIUM",
    )
    assert "5,000.00 rupees to Ravi Kumar" in summary["speech_text"]
    assert "Medium" in summary["speech_text"]
    assert "higher than your usual" in summary["speech_text"]


def test_voice_summary_generation_critical_risk():
    provider = MockVoiceProvider()
    summary = provider.generate_transaction_speech_summary(
        amount=Decimal("60000.00"),
        currency="INR",
        beneficiary_name="Unknown",
        risk_level="CRITICAL",
    )
    assert "stopped for your security" in summary["speech_text"]


@pytest.mark.asyncio
async def test_api_synthesize_summary_endpoint(client: AsyncClient):
    token = await register_and_login(client, USER1)

    # Create transaction
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "5000.00", "intent": "TRANSFER", "beneficiary_name": "Ravi Kumar"},
    )
    tx_id = tx_resp.json()["id"]

    # Assess risk
    await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Request voice summary and captions
    voice_resp = await client.post(
        "/api/v1/voice/synthesize-summary",
        headers={"Authorization": f"Bearer {token}"},
        json={"transaction_id": tx_id},
    )
    assert voice_resp.status_code == 200
    data = voice_resp.json()
    assert "5,000.00" in data["speech_text"]
    assert "Ravi Kumar" in data["speech_text"]
    assert "caption_text" in data
    assert "confirm_prompt" in data
