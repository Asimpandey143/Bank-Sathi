"""
Transaction API Endpoints

Routes:
- POST /api/v1/transactions/draft: Create transaction draft
- GET /api/v1/transactions: List user's transactions
- GET /api/v1/transactions/{id}: Get safe transaction status
- POST /api/v1/transactions/{id}/cancel: Cancel non-final transaction
- POST /api/v1/transactions/{id}/confirm: User-only confirmation & execution

CRITICAL RULES:
- Every protected endpoint validates JWT
- Ownership/authorization is checked server-side
- Client-provided risk scores or "approved" flags are ignored
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.transaction import (
    RiskAssessRequest,
    TransactionConfirmRequest,
    TransactionDraftCreate,
    TransactionResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/draft",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction draft",
)
async def create_draft(
    body: TransactionDraftCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    svc = TransactionService(db)
    tx = await svc.create_draft(
        user_id=current_user.id,
        intent=body.intent,
        amount=body.amount,
        currency=body.currency,
        beneficiary_id=body.beneficiary_id,
        beneficiary_name=body.beneficiary_name,
        raw_input=body.raw_input,
    )
    return TransactionResponse.model_validate(tx)


@router.get(
    "",
    response_model=list[TransactionResponse],
    summary="List transactions",
)
async def list_transactions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TransactionResponse]:
    svc = TransactionService(db)
    txs = await svc.list_transactions(user_id=current_user.id, limit=limit, offset=offset)
    return [TransactionResponse.model_validate(tx) for tx in txs]


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction status",
)
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    svc = TransactionService(db)
    tx = await svc.get_transaction(transaction_id=transaction_id, user_id=current_user.id)
    resp = TransactionResponse.model_validate(tx)
    try:
        from app.services.trusted_circle_service import TrustedCircleService
        tc_service = TrustedCircleService(db)
        resp.second_opinion = await tc_service.get_second_opinion_for_transaction(tx.id)
    except Exception:
        pass
    return resp


@router.post(
    "/{transaction_id}/cancel",
    response_model=TransactionResponse,
    summary="Cancel transaction",
)
async def cancel_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    svc = TransactionService(db)
    tx = await svc.cancel_transaction(
        transaction_id=transaction_id, user_id=current_user.id
    )
    return TransactionResponse.model_validate(tx)


@router.post(
    "/{transaction_id}/risk-assess",
    response_model=TransactionResponse,
    summary="Run deterministic risk assessment",
)
async def assess_risk(
    transaction_id: uuid.UUID,
    body: RiskAssessRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    svc = TransactionService(db)
    req = body or RiskAssessRequest()
    tx = await svc.assess_risk(
        transaction_id=transaction_id,
        user_id=current_user.id,
        is_untrusted_device=req.is_untrusted_device,
        is_unusual_time=req.is_unusual_time,
    )
    return TransactionResponse.model_validate(tx)


@router.post(
    "/{transaction_id}/confirm",
    response_model=TransactionResponse,
    summary="User confirmation & execution",
)
async def confirm_transaction(
    transaction_id: uuid.UUID,
    body: TransactionConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Final user confirmation. Executes money transfer via MockBankingProvider.
    Requires transaction to be in AWAITING_CONFIRMATION state.
    """
    svc = TransactionService(db)
    tx = await svc.confirm_and_execute(
        transaction_id=transaction_id, user_id=current_user.id
    )
    return TransactionResponse.model_validate(tx)
