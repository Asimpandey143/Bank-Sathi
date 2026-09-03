"""
Phase 7 tests — Community Sessions & Privacy Protection

Tests:
- Host creates a digital literacy community session
- Users list available sessions
- User joins a community session
- PRIVACY GUARANTEE: Community session details contain NO personal banking data,
  balances, transactions, or credentials of any participant.
"""
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient

HOST_USER = {
    "phone": "9999999601",
    "name": "Community Leader Ramesh",
    "password": "password123",
}

STUDENT_USER = {
    "phone": "9999999602",
    "name": "Elderly Student Sita",
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
async def test_create_and_list_community_sessions(client: AsyncClient):
    host_token = await register_and_login(client, HOST_USER)
    student_token = await register_and_login(client, STUDENT_USER)

    # 1. Host creates a session
    scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    create_resp = await client.post(
        "/api/v1/community/sessions",
        headers={"Authorization": f"Bearer {host_token}"},
        json={
            "topic": "Safe Digital Payments for Seniors",
            "description": "Learn how to verify payment details and stay safe from scams.",
            "scheduled_at": scheduled_time,
            "max_participants": 25,
            "duration_minutes": 45,
        },
    )
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["topic"] == "Safe Digital Payments for Seniors"
    assert created_data["status"] == "scheduled"
    session_id = created_data["id"]

    # 2. Student lists available sessions
    list_resp = await client.get(
        "/api/v1/community/sessions",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert len(sessions) >= 1
    session_ids = [s["id"] for s in sessions]
    assert session_id in session_ids

    # 3. Student joins the session
    join_resp = await client.post(
        f"/api/v1/community/sessions/{session_id}/join",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert join_resp.status_code == 200
    join_data = join_resp.json()
    assert join_data["session_id"] == session_id
    assert "Privacy protection active" in join_data["message"]

    # PRIVACY AUDIT: Ensure no sensitive user data is returned
    for key in ("balance", "transactions", "otp", "pin", "phone", "password"):
        assert key not in join_data
        assert key not in created_data
