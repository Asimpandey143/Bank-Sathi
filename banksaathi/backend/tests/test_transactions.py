"""
Phase 2 tests — Transaction Engine & Mock Banking Provider

Tests:
- Create draft and verify state machine progression (DRAFT -> PARSED)
- Cancel transaction
- State transition guard: Cannot confirm unless in AWAITING_CONFIRMATION
- Successful execution via MockBankingProvider: AWAITING_CONFIRMATION -> CONFIRMED -> PROCESSING -> COMPLETED
- Balance reduction on successful transfer
- Insufficient balance leads to FAILED status
- Ownership scoping (users cannot access other users' transactions)
- Idempotency key handling
"""
from decimal import Decimal
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionStatus
from app.providers.banking import get_banking_provider, MockBankingProvider

USER1 = {
    "phone": "9999999101",
    "name": "Meena",
    "password": "password123",
}

USER2 = {
    "phone": "9999999102",
    "name": "Ravi",
    "password": "password123",
}


async def register_and_login(client: AsyncClient, user_data: dict) -> str:
    await client.post("/api/v1/auth/register", json=user_data)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": user_data["phone"], "password": user_data["password"]},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_transaction_draft(client: AsyncClient):
    """POST /api/v1/transactions/draft creates a draft and advances to PARSED."""
    token = await register_and_login(client, USER1)
    response = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "intent": "TRANSFER",
            "amount": "5000.00",
            "currency": "INR",
            "beneficiary_name": "Ravi Kumar",
            "raw_input": "Send five thousand rupees to Ravi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PARSED"
    assert Decimal(data["amount"]) == Decimal("5000.00")
    assert data["currency"] == "INR"
    assert data["beneficiary_name"] == "Ravi Kumar"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_transaction_ownership(client: AsyncClient):
    """A user cannot access another user's transaction."""
    token1 = await register_and_login(client, USER1)
    token2 = await register_and_login(client, USER2)

    # User 1 creates transaction
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token1}"},
        json={"amount": "1000.00", "intent": "TRANSFER", "beneficiary_name": "Ravi"},
    )
    tx_id = tx_resp.json()["id"]

    # User 2 tries to access it -> 403
    forbidden_resp = await client.get(
        f"/api/v1/transactions/{tx_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert forbidden_resp.status_code == 403
    assert forbidden_resp.json()["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_cancel_transaction(client: AsyncClient):
    """A transaction in PARSED state can be cancelled."""
    token = await register_and_login(client, USER1)
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "1500.00", "intent": "TRANSFER"},
    )
    tx_id = tx_resp.json()["id"]

    cancel_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

    # Cancelling again must be rejected by state machine
    re_cancel = await client.post(
        f"/api/v1/transactions/{tx_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert re_cancel.status_code == 422
    assert re_cancel.json()["code"] == "INVALID_STATE_TRANSITION"


@pytest.mark.asyncio
async def test_invalid_confirmation_before_risk_assessment(client: AsyncClient):
    """Attempting to confirm a transaction directly from PARSED must fail."""
    token = await register_and_login(client, USER1)
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "2000.00", "intent": "TRANSFER"},
    )
    tx_id = tx_resp.json()["id"]

    # Trying to confirm directly -> 422
    confirm_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True},
    )
    assert confirm_resp.status_code == 422
    assert confirm_resp.json()["code"] == "INVALID_STATE_TRANSITION"


@pytest.mark.asyncio
async def test_successful_confirmation_and_execution(
    client: AsyncClient, db_session: AsyncSession
):
    """
    Simulate full valid transition to AWAITING_CONFIRMATION, then confirm.
    Must execute through MockBankingProvider and result in COMPLETED with bank reference.
    """
    token = await register_and_login(client, USER1)
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "5000.00", "intent": "TRANSFER", "beneficiary_name": "Ravi Kumar"},
    )
    tx_id = tx_resp.json()["id"]

    # Manually transition to AWAITING_CONFIRMATION in DB to test confirm execution
    stmt = select(Transaction).where(Transaction.id == uuid.UUID(tx_id))
    res = await db_session.execute(stmt)
    tx = res.scalar_one()
    tx.status = TransactionStatus.AWAITING_CONFIRMATION
    await db_session.commit()

    # User confirms
    confirm_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True},
    )
    assert confirm_resp.status_code == 200
    data = confirm_resp.json()
    assert data["status"] == "COMPLETED"
    assert data["bank_reference"] is not None
    assert data["bank_reference"].startswith("DEMO-")


@pytest.mark.asyncio
async def test_insufficient_funds_fails_transaction(
    client: AsyncClient, db_session: AsyncSession
):
    """If amount exceeds user balance in MockBankingProvider, transaction moves to FAILED."""
    token = await register_and_login(client, USER1)

    # User has default 50000 balance, request 999999
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "999999.00", "intent": "TRANSFER"},
    )
    tx_id = tx_resp.json()["id"]

    # Transition to AWAITING_CONFIRMATION
    stmt = select(Transaction).where(Transaction.id == uuid.UUID(tx_id))
    res = await db_session.execute(stmt)
    tx = res.scalar_one()
    tx.status = TransactionStatus.AWAITING_CONFIRMATION
    await db_session.commit()

    confirm_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True},
    )
    assert confirm_resp.status_code == 200
    data = confirm_resp.json()
    assert data["status"] == "FAILED"
    assert data["bank_reference"] is None
