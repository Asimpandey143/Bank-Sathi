"""
Phase 3 tests — Deterministic Risk Engine & Risk Assessment API

Tests all policy cases specified in PRD.md, AI_ENGINE.md, and TESTING.md:
- Case 1: Normal payment within historical pattern => LOW
- Case 2: Unusual amount (> 2x average) => MEDIUM
- Case 3: High amount + new beneficiary + untrusted device => HIGH / CRITICAL
- Case 4: Exceeds daily transaction limit => CRITICAL (blocked)
- API test: POST /transactions/{id}/risk-assess updates state to AWAITING_CONFIRMATION
- Security test: CRITICAL risk blocks transaction; confirmation on BLOCKED transaction is rejected
- Full flow: DRAFT -> PARSED -> RISK_ASSESSED -> AWAITING_CONFIRMATION -> CONFIRMED -> COMPLETED
"""
from decimal import Decimal
import uuid
import pytest
from httpx import AsyncClient

from app.models.transaction import TransactionStatus
from app.services.risk_engine import RiskContext, RiskEngine, RiskLevel

USER1 = {
    "phone": "9999999201",
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


# ── Unit tests for RiskEngine ────────────────────────────────────────────────

def test_risk_case_1_normal_transaction():
    """
    Case 1 (from TESTING.md):
    usual = 1500, current = 1000, known beneficiary, trusted device => LOW
    """
    engine = RiskEngine()
    ctx = RiskContext(
        amount=Decimal("1000.00"),
        average_amount=Decimal("1500.00"),
        beneficiary_is_new=False,
        is_untrusted_device=False,
        is_unusual_time=False,
    )
    decision = engine.evaluate(ctx)
    assert decision.level == RiskLevel.LOW
    assert decision.score < 25
    assert not decision.is_blocked


def test_risk_case_2_unusual_amount():
    """
    Case 2 (from TESTING.md):
    usual = 1500, current = 5000, known beneficiary, trusted device => MEDIUM
    """
    engine = RiskEngine()
    ctx = RiskContext(
        amount=Decimal("5000.00"),
        average_amount=Decimal("1500.00"),
        beneficiary_is_new=False,
        is_untrusted_device=False,
        is_unusual_time=False,
    )
    decision = engine.evaluate(ctx)
    assert decision.level == RiskLevel.MEDIUM
    assert 25 <= decision.score < 50
    assert not decision.is_blocked
    assert any("higher than your recent average" in r for r in decision.reasons)


def test_risk_case_3_dangerous_combination():
    """
    Case 3 (from TESTING.md):
    new beneficiary, large amount (5000 vs 1500), untrusted device => HIGH / CRITICAL
    """
    engine = RiskEngine()
    ctx = RiskContext(
        amount=Decimal("5000.00"),
        average_amount=Decimal("1500.00"),
        beneficiary_is_new=True,
        is_untrusted_device=True,
        is_unusual_time=False,
    )
    decision = engine.evaluate(ctx)
    # Deviation (30) + New beneficiary (25) + Untrusted device (30) = 85 -> CRITICAL
    assert decision.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert decision.score >= 50
    assert len(decision.reasons) >= 2


def test_risk_case_4_daily_limit_exceeded():
    """Amount exceeding remaining daily limit must immediately result in CRITICAL/BLOCKED."""
    engine = RiskEngine()
    ctx = RiskContext(
        amount=Decimal("60000.00"),
        average_amount=Decimal("1500.00"),
        daily_spent_so_far=Decimal("0.00"),
        daily_limit=Decimal("50000.00"),
    )
    decision = engine.evaluate(ctx)
    assert decision.level == RiskLevel.CRITICAL
    assert decision.score == 100
    assert decision.is_blocked


def test_risk_unusual_time_weight():
    """Unusual time adds appropriate weight."""
    engine = RiskEngine()
    ctx = RiskContext(
        amount=Decimal("1000.00"),
        average_amount=Decimal("1500.00"),
        is_unusual_time=True,
    )
    decision = engine.evaluate(ctx)
    assert decision.score == 10
    assert decision.level == RiskLevel.LOW
    assert any("unusual time" in r for r in decision.reasons)


# ── API tests for Risk Assessment endpoint ───────────────────────────────────

@pytest.mark.asyncio
async def test_api_risk_assess_transitions_to_awaiting_confirmation(client: AsyncClient):
    """
    POST /api/v1/transactions/{id}/risk-assess:
    Assesses risk and transitions status to AWAITING_CONFIRMATION.
    """
    token = await register_and_login(client, USER1)

    # 1. Create draft
    draft_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "intent": "TRANSFER",
            "amount": "5000.00",
            "currency": "INR",
            "beneficiary_name": "Ravi Kumar",
        },
    )
    assert draft_resp.status_code == 201
    tx_id = draft_resp.json()["id"]

    # 2. Risk assess (amount 5000 > baseline 1500*2 -> MEDIUM risk)
    risk_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert risk_resp.status_code == 200
    data = risk_resp.json()
    assert data["status"] == "AWAITING_CONFIRMATION"
    assert data["risk_level"] in ("MEDIUM", "HIGH")
    assert data["risk_score"] is not None
    assert data["risk_reasons"] is not None
    assert len(data["risk_reasons"]["reasons"]) > 0


@pytest.mark.asyncio
async def test_api_critical_risk_blocks_transaction(client: AsyncClient):
    """
    A transaction triggering CRITICAL risk (e.g. over daily limit) transitions to BLOCKED.
    Attempting to confirm a BLOCKED transaction must return 422.
    """
    token = await register_and_login(client, USER1)

    # 1. Create draft with amount over daily limit (60,000 > 50,000)
    draft_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "intent": "TRANSFER",
            "amount": "60000.00",
            "currency": "INR",
        },
    )
    tx_id = draft_resp.json()["id"]

    # 2. Risk assess -> must move to BLOCKED
    risk_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert risk_resp.status_code == 200
    data = risk_resp.json()
    assert data["status"] == "BLOCKED"
    assert data["risk_level"] == "CRITICAL"
    assert data["risk_score"] == 100

    # 3. Attempting to confirm a BLOCKED transaction must be rejected
    confirm_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True},
    )
    assert confirm_resp.status_code == 422
    assert confirm_resp.json()["code"] == "TRANSACTION_NOT_CONFIRMABLE"


@pytest.mark.asyncio
async def test_full_transaction_flow_draft_to_completed(client: AsyncClient):
    """
    Full happy path through state machine:
    DRAFT -> PARSED -> RISK_ASSESSED -> AWAITING_CONFIRMATION -> CONFIRMED -> PROCESSING -> COMPLETED
    """
    token = await register_and_login(client, USER1)

    # First add a known beneficiary
    b_resp = await client.post(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Ravi Kumar", "masked_account": "****4321"},
    )
    b_id = b_resp.json()["id"]

    # 1. Create draft
    draft_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "intent": "TRANSFER",
            "amount": "1000.00",
            "currency": "INR",
            "beneficiary_id": b_id,
        },
    )
    assert draft_resp.status_code == 201
    tx_id = draft_resp.json()["id"]
    assert draft_resp.json()["status"] == "PARSED"

    # 2. Risk assess (1000 is below baseline 1500 -> LOW)
    risk_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert risk_resp.status_code == 200
    assert risk_resp.json()["status"] == "AWAITING_CONFIRMATION"

    # 3. Confirm and execute
    confirm_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True},
    )
    assert confirm_resp.status_code == 200
    final_data = confirm_resp.json()
    assert final_data["status"] == "COMPLETED"
    assert final_data["bank_reference"] is not None
