"""
Helper API Routes & WebSocket

Implements the "Shared guidance, not shared access" principle.

SECURITY RULES:
- Helper cannot approve transactions
- Helper cannot execute transactions
- Helper cannot modify amounts or beneficiaries
- Helper cannot view OTP, PIN, passwords, or credentials
- Session expiration is strictly enforced
"""
import uuid

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
from app.schemas.helper import (
    HelperAbstractedView,
    HelperInvitationCreate,
    HelperInvitationResponse,
    HelperSessionCreate,
    HelperSessionResponse,
)
from app.services.helper_service import HelperService

router = APIRouter(prefix="/helpers", tags=["Helpers"])


@router.post(
    "/invitations",
    response_model=HelperInvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create helper invitation",
)
async def create_invitation(
    body: HelperInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HelperInvitationResponse:
    svc = HelperService(db)
    assignment = await svc.create_invitation(
        user_id=current_user.id, helper_phone=body.helper_phone
    )
    return HelperInvitationResponse.model_validate(assignment)


@router.post(
    "/invitations/{invitation_id}/accept",
    response_model=HelperInvitationResponse,
    summary="Accept helper invitation",
)
async def accept_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HelperInvitationResponse:
    svc = HelperService(db)
    assignment = await svc.accept_invitation(
        assignment_id=invitation_id, helper_user_id=current_user.id
    )
    return HelperInvitationResponse.model_validate(assignment)


@router.post(
    "/sessions",
    response_model=HelperSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create temporary helper session",
)
async def create_session(
    body: HelperSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HelperSessionResponse:
    svc = HelperService(db)
    session = await svc.create_session(
        user_id=current_user.id,
        helper_user_id=body.helper_user_id,
        duration_minutes=body.duration_minutes,
    )
    return HelperSessionResponse.model_validate(session)


@router.get(
    "/sessions/{session_id}/view",
    response_model=HelperAbstractedView,
    summary="Get abstracted guidance view (no secrets)",
)
async def get_abstracted_view(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HelperAbstractedView:
    """
    Returns safe, abstracted transaction status for the helper.
    Excludes OTP, PIN, password, credentials.
    """
    svc = HelperService(db)
    return await svc.get_abstracted_view(
        session_id=session_id, helper_user_id=current_user.id
    )


@router.post(
    "/sessions/{session_id}/pause",
    response_model=HelperSessionResponse,
    summary="Pause helper session",
)
async def pause_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HelperSessionResponse:
    svc = HelperService(db)
    session = await svc.pause_session(
        session_id=session_id, actor_user_id=current_user.id
    )
    return HelperSessionResponse.model_validate(session)


# ── WebSocket for real-time abstracted guidance ──────────────────────────────
@router.websocket("/ws/{session_id}")
async def helper_websocket(websocket: WebSocket, session_id: uuid.UUID):
    """
    Real-time WebSocket connection for helper guidance.
    Broadcasts abstracted status updates to the helper.
    Never broadcasts OTP, PIN, passwords, or credentials.
    """
    await websocket.accept()
    try:
        # Send initial connected message
        await websocket.send_json({
            "event": "connected",
            "session_id": str(session_id),
            "message": "Connected to BankSathi Helper Guidance Channel. Shared guidance active.",
        })
        while True:
            # Receive ping or helper guidance acknowledgement
            data = await websocket.receive_text()
            # Echo back safe acknowledgement
            await websocket.send_json({
                "event": "guidance_ack",
                "session_id": str(session_id),
                "status": "active",
            })
    except WebSocketDisconnect:
        pass
