"""
Health check endpoint.

Returns {"status": "ok"} when the backend is running.
Used by Docker Compose healthcheck and load balancers.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    Returns service health status.
    Used by Docker Compose healthcheck.
    """
    return HealthResponse(status="ok")
