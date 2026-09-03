"""
Phase 1 tests — User preferences and beneficiaries.

Tests:
- Get accessibility preferences
- Update preferences
- Add beneficiary
- List beneficiaries
"""
import pytest
from httpx import AsyncClient

DEMO_USER = {
    "phone": "9999999002",
    "name": "Meena",
    "password": "testpass123",
}


async def get_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/register", json=DEMO_USER)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": DEMO_USER["phone"], "password": DEMO_USER["password"]},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_get_default_accessibility_preferences(client: AsyncClient):
    """GET /api/v1/users/me/preferences returns defaults after registration."""
    token = await get_token(client)
    response = await client.get(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert data["font_scale"] == 1.0
    assert data["high_contrast"] is False
    assert data["confirmation_mode"] == "single"


@pytest.mark.asyncio
async def test_update_accessibility_preferences(client: AsyncClient):
    """PATCH /api/v1/users/me/preferences updates preferences."""
    token = await get_token(client)
    response = await client.patch(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "font_scale": 1.5,
            "high_contrast": True,
            "confirmation_mode": "double",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["font_scale"] == 1.5
    assert data["high_contrast"] is True
    assert data["confirmation_mode"] == "double"


@pytest.mark.asyncio
async def test_add_beneficiary(client: AsyncClient):
    """POST /api/v1/users/me/beneficiaries creates a beneficiary."""
    token = await get_token(client)
    response = await client.post(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Ravi Kumar", "masked_account": "****1234"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["display_name"] == "Ravi Kumar"
    assert data["trust_level"] == "new"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_beneficiaries(client: AsyncClient):
    """GET /api/v1/users/me/beneficiaries returns user's beneficiaries."""
    token = await get_token(client)
    # Add two beneficiaries
    await client.post(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Ravi Kumar", "masked_account": "****1234"},
    )
    await client.post(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Priya Sharma", "masked_account": "****5678"},
    )

    response = await client.get(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [b["display_name"] for b in data]
    assert "Ravi Kumar" in names
    assert "Priya Sharma" in names


@pytest.mark.asyncio
async def test_beneficiaries_are_user_scoped(client: AsyncClient):
    """User can only see their own beneficiaries."""
    # Register two users
    token1 = await get_token(client)
    await client.post("/api/v1/auth/register", json={
        "phone": "9999999003",
        "name": "Other User",
        "password": "testpass123",
    })
    login2 = await client.post("/api/v1/auth/login", json={
        "phone": "9999999003",
        "password": "testpass123",
    })
    token2 = login2.json()["access_token"]

    # User 1 adds a beneficiary
    await client.post(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token1}"},
        json={"display_name": "User1's Contact", "masked_account": "****9999"},
    )

    # User 2 sees no beneficiaries
    response = await client.get(
        "/api/v1/users/me/beneficiaries",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 200
    assert response.json() == []
