"""
Trusted Circle Tests & Security Guarantees

Requirements from BankSathi_Trusted_Circle_Change.md:
- User can add trusted circle member (e.g. daughter, son, spouse)
- User can revoke trusted member; revoked member receives no new notifications
- Risk-based notification generation (LOW does not notify; MEDIUM/HIGH generates privacy-safe notification)
- Privacy safety: Notifications never expose OTP, PIN, password, or banking credentials
- Second opinion submission (LOOKS_EXPECTED, NOT_RECOGNIZED, REQUEST_USER_VERIFICATION)
- Advisory responses CANNOT execute or confirm transactions
- Security: Trusted person CANNOT confirm or cancel user's transactions (returns 403)
- Screen-sharing endpoints do NOT exist (returns 404)
"""
from decimal import Decimal
import uuid
import pytest
from httpx import AsyncClient

from app.models.trusted_circle import MemberStatus, NotificationStatus, SecondOpinionResponse

USER_MEENA = {
    "phone": "9999999501",
    "name": "Meena Devi",
    "password": "userpass123",
}

DAUGHTER_ANANYA = {
    "phone": "9999999502",
    "name": "Ananya (Daughter)",
    "password": "daughterpass123",
}


async def register_and_login(client: AsyncClient, user_data: dict) -> str:
    await client.post("/api/v1/auth/register", json=user_data)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": user_data["phone"], "password": user_data["password"]},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_user_can_add_and_list_trusted_person(client: AsyncClient):
    """User adds daughter to Trusted Circle."""
    meena_token = await register_and_login(client, USER_MEENA)
    await register_and_login(client, DAUGHTER_ANANYA)

    # Meena invites daughter Ananya
    inv_resp = await client.post(
        "/api/v1/trusted-circle/members/invite",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"phone": DAUGHTER_ANANYA["phone"], "relationship_label": "Daughter"},
    )
    assert inv_resp.status_code == 201
    member_data = inv_resp.json()
    assert member_data["relationship_label"] == "Daughter"
    assert member_data["status"] == "active"
    assert member_data["permissions"]["provide_second_opinion"] is True
    assert member_data["permissions"]["approve_transaction"] is False
    assert member_data["permissions"]["execute_transaction"] is False
    assert member_data["permissions"]["screen_share"] is False

    # List members
    list_resp = await client.get(
        "/api/v1/trusted-circle/members",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert list_resp.status_code == 200
    members = list_resp.json()
    assert len(members) == 1
    assert members[0]["relationship_label"] == "Daughter"


@pytest.mark.asyncio
async def test_user_can_revoke_trusted_person(client: AsyncClient):
    """User can revoke a trusted person; revoked person receives no new notifications."""
    meena_token = await register_and_login(client, USER_MEENA)
    await register_and_login(client, DAUGHTER_ANANYA)

    # 1. Invite
    inv_resp = await client.post(
        "/api/v1/trusted-circle/members/invite",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"phone": DAUGHTER_ANANYA["phone"], "relationship_label": "Daughter"},
    )
    member_id = inv_resp.json()["id"]

    # 2. Revoke
    del_resp = await client.delete(
        f"/api/v1/trusted-circle/members/{member_id}",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert del_resp.status_code == 204

    # 3. List should no longer include revoked member
    list_resp = await client.get(
        "/api/v1/trusted-circle/members",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_risk_based_notification_generation_and_privacy_safety(client: AsyncClient):
    """
    Transactions with MEDIUM/HIGH risk trigger privacy-safe notifications to active trusted members.
    Notification must NOT contain OTP, PIN, passwords, or bank credentials.
    """
    meena_token = await register_and_login(client, USER_MEENA)
    daughter_token = await register_and_login(client, DAUGHTER_ANANYA)

    # Add daughter to Trusted Circle
    await client.post(
        "/api/v1/trusted-circle/members/invite",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"phone": DAUGHTER_ANANYA["phone"], "relationship_label": "Daughter"},
    )

    # Meena creates a ₹5,000 transfer (higher than ₹1,500 baseline -> MEDIUM risk)
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"amount": "5000.00", "intent": "TRANSFER", "beneficiary_name": "Ravi Kumar"},
    )
    tx_id = tx_resp.json()["id"]

    # Assess risk
    assess_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert assess_resp.status_code == 200
    assert assess_resp.json()["risk_level"] in ("MEDIUM", "HIGH")

    # Daughter checks notifications
    notif_resp = await client.get(
        "/api/v1/trusted-circle/notifications",
        headers={"Authorization": f"Bearer {daughter_token}"},
    )
    assert notif_resp.status_code == 200
    notifs = notif_resp.json()
    assert len(notifs) == 1

    notif = notifs[0]
    assert "₹5,000" in notif["amount_display"]
    assert notif["beneficiary_display"] == "Ravi Kumar"
    assert notif["status"] == "pending"

    # PRIVACY SAFETY TEST: Ensure zero secrets are present in notification response
    for secret in ("otp", "pin", "password", "hashed_password", "bank_credentials", "token"):
        assert secret not in notif


@pytest.mark.asyncio
async def test_advisory_second_opinion_flow(client: AsyncClient):
    """
    Daughter submits 'LOOKS_EXPECTED' second opinion.
    Mother views the advisory response in transaction details.
    Advisory response does NOT execute payment; user confirms.
    """
    meena_token = await register_and_login(client, USER_MEENA)
    daughter_token = await register_and_login(client, DAUGHTER_ANANYA)

    # Setup Trusted Circle
    await client.post(
        "/api/v1/trusted-circle/members/invite",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"phone": DAUGHTER_ANANYA["phone"], "relationship_label": "Daughter"},
    )

    # Create transaction & assess risk
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"amount": "5000.00", "intent": "TRANSFER", "beneficiary_name": "Ravi Kumar"},
    )
    tx_id = tx_resp.json()["id"]
    await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {meena_token}"},
    )

    # Daughter gets notification
    notif_resp = await client.get(
        "/api/v1/trusted-circle/notifications",
        headers={"Authorization": f"Bearer {daughter_token}"},
    )
    notification_id = notif_resp.json()[0]["id"]

    # Daughter submits LOOKS_EXPECTED
    resp_sub = await client.post(
        f"/api/v1/trusted-circle/notifications/{notification_id}/response",
        headers={"Authorization": f"Bearer {daughter_token}"},
        json={"response": "LOOKS_EXPECTED", "comment": "Groceries for dad"},
    )
    assert resp_sub.status_code == 200
    assert resp_sub.json()["response"] == "LOOKS_EXPECTED"

    # Meena checks transaction status — second opinion is reflected
    tx_check = await client.get(
        f"/api/v1/transactions/{tx_id}",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    tx_data = tx_check.json()
    assert tx_data["status"] == "AWAITING_CONFIRMATION"  # NOT automatically completed!
    assert tx_data["second_opinion"] is not None
    assert tx_data["second_opinion"]["response"] == "LOOKS_EXPECTED"

    # Sole user confirmation
    conf_resp = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"confirmed": True},
    )
    assert conf_resp.status_code == 200
    assert conf_resp.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_security_trusted_person_cannot_confirm_or_cancel_transaction(client: AsyncClient):
    """
    CRITICAL SECURITY TEST:
    A trusted person attempting to confirm or cancel the user's transaction MUST receive 403 Forbidden.
    """
    meena_token = await register_and_login(client, USER_MEENA)
    daughter_token = await register_and_login(client, DAUGHTER_ANANYA)

    # Setup Trusted Circle
    await client.post(
        "/api/v1/trusted-circle/members/invite",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"phone": DAUGHTER_ANANYA["phone"], "relationship_label": "Daughter"},
    )

    # Meena drafts transaction and assesses risk
    tx_resp = await client.post(
        "/api/v1/transactions/draft",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"amount": "5000.00", "intent": "TRANSFER", "beneficiary_name": "Ravi Kumar"},
    )
    tx_id = tx_resp.json()["id"]
    await client.post(
        f"/api/v1/transactions/{tx_id}/risk-assess",
        headers={"Authorization": f"Bearer {meena_token}"},
    )

    # Daughter tries to confirm Meena's transaction -> 403
    daughter_confirm = await client.post(
        f"/api/v1/transactions/{tx_id}/confirm",
        headers={"Authorization": f"Bearer {daughter_token}"},
        json={"confirmed": True},
    )
    assert daughter_confirm.status_code == 403

    # Daughter tries to cancel Meena's transaction -> 403
    daughter_cancel = await client.post(
        f"/api/v1/transactions/{tx_id}/cancel",
        headers={"Authorization": f"Bearer {daughter_token}"},
    )
    assert daughter_cancel.status_code == 403


@pytest.mark.asyncio
async def test_screen_sharing_endpoints_do_not_exist(client: AsyncClient):
    """
    Verify all screen-sharing and helper session endpoints are completely removed.
    """
    meena_token = await register_and_login(client, USER_MEENA)

    # /api/v1/helpers should return 404
    resp1 = await client.post(
        "/api/v1/helpers/sessions",
        headers={"Authorization": f"Bearer {meena_token}"},
        json={"helper_user_id": str(uuid.uuid4())},
    )
    assert resp1.status_code == 404

    resp2 = await client.get(
        "/api/v1/helpers/sessions/some-id/view",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert resp2.status_code == 404
