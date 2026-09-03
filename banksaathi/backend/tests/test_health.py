"""
PHASE 0 tests — Health endpoint and application startup.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """GET /health must return {"status": "ok"}."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_check_is_unauthenticated(client: AsyncClient):
    """Health check must not require authentication."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client: AsyncClient):
    """Unknown routes must return a consistent error format."""
    response = await client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    data = response.json()
    assert "code" in data or "detail" in data  # FastAPI default or our handler
