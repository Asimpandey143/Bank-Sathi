"""
Phase 1 tests — Authentication endpoints.

Tests:
- Register a new user
- Cannot register duplicate phone
- Login with correct credentials
- Login fails with wrong password
- Protected endpoint requires valid JWT
"""
import pytest
from httpx import AsyncClient


DEMO_USER = {
    "phone": "9999999001",
    "name": "Test User",
    "password": "testpass123",
}


@pytest.mark.asyncio
async def test_register_creates_user(client: AsyncClient):
    """POST /api/v1/auth/register creates a new user."""
    response = await client.post("/api/v1/auth/register", json=DEMO_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["role"] == "user"
    assert "id" in data
    # SECURITY: hashed_password must NEVER appear in response
    assert "hashed_password" not in data
    assert "password" not in data
    assert "phone_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_phone_fails(client: AsyncClient):
    """Cannot register the same phone number twice."""
    await client.post("/api/v1/auth/register", json=DEMO_USER)
    response = await client.post("/api/v1/auth/register", json=DEMO_USER)
    assert response.status_code == 409
    data = response.json()
    assert data["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_login_returns_token(client: AsyncClient):
    """POST /api/v1/auth/login returns a JWT on correct credentials."""
    await client.post("/api/v1/auth/register", json=DEMO_USER)
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": DEMO_USER["phone"], "password": DEMO_USER["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_fails(client: AsyncClient):
    """Login fails with incorrect password — returns 401."""
    await client.post("/api/v1/auth/register", json=DEMO_USER)
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": DEMO_USER["phone"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_unknown_phone_fails(client: AsyncClient):
    """Login with unknown phone returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": "0000000000", "password": "anypassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_requires_auth(client: AsyncClient):
    """GET /api/v1/users/me requires a valid JWT."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 403  # no auth header → 403 (HTTPBearer)


@pytest.mark.asyncio
async def test_get_me_with_valid_token(client: AsyncClient):
    """GET /api/v1/users/me returns user profile with valid JWT."""
    # Register
    await client.post("/api/v1/auth/register", json=DEMO_USER)
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"phone": DEMO_USER["phone"], "password": DEMO_USER["password"]},
    )
    token = login_response.json()["access_token"]

    # Use token
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert "hashed_password" not in data
