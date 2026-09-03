"""
Community Session API Routes & WebSocket

Group digital banking literacy sessions (WORKFLOWS.md - Workflow E).

PRIVACY RULE:
Never exposes or broadcasts personal banking information, balances, or transactions.
"""
import uuid
from pydantic import BaseModel
from fastapi import (
    APIRouter,
    Depends,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.community import (
    CommunitySessionCreate,
    CommunitySessionResponse,
)
from app.services.community_service import CommunityService

router = APIRouter(prefix="/community", tags=["Community"])


class JoinResponse(BaseModel):
    session_id: uuid.UUID
    topic: str
    status: str
    message: str


@router.get(
    "/sessions",
    response_model=list[CommunitySessionResponse],
    summary="List available community sessions",
)
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CommunitySessionResponse]:
    svc = CommunityService(db)
    sessions = await svc.list_sessions(limit=limit, offset=offset)
    return [CommunitySessionResponse.model_validate(s) for s in sessions]


@router.post(
    "/sessions",
    response_model=CommunitySessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a community session",
)
async def create_session(
    body: CommunitySessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommunitySessionResponse:
    svc = CommunityService(db)
    session = await svc.create_session(
        host_id=current_user.id,
        topic=body.topic,
        description=body.description,
        scheduled_at=body.scheduled_at,
        max_participants=body.max_participants,
        duration_minutes=body.duration_minutes,
    )
    return CommunitySessionResponse.model_validate(session)


@router.get(
    "/sessions/{session_id}",
    response_model=CommunitySessionResponse,
    summary="Get community session details",
)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommunitySessionResponse:
    svc = CommunityService(db)
    session = await svc.get_session(session_id)
    return CommunitySessionResponse.model_validate(session)


@router.post(
    "/sessions/{session_id}/join",
    response_model=JoinResponse,
    summary="Join a community session",
)
async def join_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JoinResponse:
    svc = CommunityService(db)
    res = await svc.join_session(session_id, current_user.id)
    return JoinResponse(**res)


@router.websocket("/ws/{session_id}")
async def community_websocket(websocket: WebSocket, session_id: uuid.UUID):
    """
    WebSocket channel for community learning session chat / slide synchronization.
    Strictly isolated from personal financial transactions.
    """
    await websocket.accept()
    try:
        await websocket.send_json({
            "event": "connected",
            "session_id": str(session_id),
            "message": "Connected to BankSathi Community Learning Session.",
        })
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "event": "echo",
                "received": data,
            })
    except WebSocketDisconnect:
        pass
