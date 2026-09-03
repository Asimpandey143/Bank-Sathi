"""
Transaction Service & Repository

Implements:
- Transaction state machine enforcement
- Server-side validation of amounts and state transitions
- Idempotency handling
- Integration with BankingProvider
- Security audit event logging

CRITICAL SAFETY RULES:
- Frontend can never supply status, risk_score, risk_level, or approval
- Only authenticated user can confirm and execute transactions
- State machine rejects invalid transitions with InvalidStateTransitionError
"""
from decimal import Decimal
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    ForbiddenError,
    InvalidStateTransitionError,
    NotFoundError,
    TransactionNotConfirmableError,
)
from app.models.beneficiary import Beneficiary
from app.models.transaction import (
    Transaction,
    TransactionStatus,
    is_valid_transition,
)
from app.providers.banking import BankingProvider, get_banking_provider
from app.services.audit_service import AuditService
from app.services.risk_engine import RiskContext, RiskEngine


class TransactionService:
    def __init__(
        self,
        db: AsyncSession,
        banking_provider: BankingProvider | None = None,
        risk_engine: RiskEngine | None = None,
    ) -> None:
        self.db = db
        self.banking_provider = banking_provider or get_banking_provider()
        self.risk_engine = risk_engine or RiskEngine()
        self.audit_service = AuditService(db)

    async def create_draft(
        self,
        user_id: uuid.UUID,
        intent: str,
        amount: Decimal,
        currency: str = "INR",
        beneficiary_id: uuid.UUID | None = None,
        beneficiary_name: str | None = None,
        raw_input: str | None = None,
    ) -> Transaction:
        """Create a new transaction in DRAFT state and move to PARSED."""
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # If beneficiary_id provided, verify it belongs to user
        if beneficiary_id is not None:
            b_stmt = select(Beneficiary).where(
                Beneficiary.id == beneficiary_id, Beneficiary.user_id == user_id
            )
            b_res = await self.db.execute(b_stmt)
            b = b_res.scalar_one_or_none()
            if not b:
                raise NotFoundError("Beneficiary")
            if not beneficiary_name:
                beneficiary_name = b.display_name

        transaction = Transaction(
            user_id=user_id,
            beneficiary_id=beneficiary_id,
            beneficiary_name=beneficiary_name,
            amount=amount,
            currency=currency,
            intent=intent,
            raw_input=raw_input,
            status=TransactionStatus.DRAFT,
        )
        self.db.add(transaction)
        await self.db.flush()

        # Advance to PARSED state
        transaction.status = TransactionStatus.PARSED

        await self.audit_service.log(
            event_type="transaction.created",
            actor_user_id=user_id,
            resource_type="transaction",
            resource_id=transaction.id,
            metadata={
                "amount": str(amount),
                "currency": currency,
                "intent": intent,
                "status": transaction.status,
            },
        )
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_transaction(
        self, transaction_id: uuid.UUID, user_id: uuid.UUID
    ) -> Transaction:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.db.execute(stmt)
        tx = result.scalar_one_or_none()
        if not tx:
            raise NotFoundError("Transaction")
        if tx.user_id != user_id:
            raise ForbiddenError("You cannot access another user's transaction.")
        return tx

    async def list_transactions(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def cancel_transaction(
        self, transaction_id: uuid.UUID, user_id: uuid.UUID, reason: str | None = None
    ) -> Transaction:
        tx = await self.get_transaction(transaction_id, user_id)

        from_status = TransactionStatus(tx.status)
        if not is_valid_transition(from_status, TransactionStatus.CANCELLED):
            raise InvalidStateTransitionError(tx.status, TransactionStatus.CANCELLED)

        tx.status = TransactionStatus.CANCELLED

        await self.audit_service.log(
            event_type="transaction.cancelled",
            actor_user_id=user_id,
            resource_type="transaction",
            resource_id=tx.id,
            metadata={"reason": reason or "User cancelled transaction."},
        )
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def assess_risk(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
        is_untrusted_device: bool = False,
        is_unusual_time: bool = False,
    ) -> Transaction:
        """
        Run deterministic risk assessment on a PARSED transaction.
        Transitions to AWAITING_CONFIRMATION (or BLOCKED if critical).
        """
        tx = await self.get_transaction(transaction_id, user_id)

        # Transition check: must be in PARSED
        current_status = TransactionStatus(tx.status)
        if current_status != TransactionStatus.PARSED:
            raise InvalidStateTransitionError(tx.status, TransactionStatus.RISK_ASSESSED)

        # Calculate average amount from past completed transactions
        past_stmt = select(Transaction.amount).where(
            Transaction.user_id == user_id,
            Transaction.status == TransactionStatus.COMPLETED,
        )
        past_res = await self.db.execute(past_stmt)
        past_amounts = past_res.scalars().all()
        if past_amounts:
            average_amount = sum(past_amounts) / len(past_amounts)
        else:
            average_amount = Decimal("1500.00")  # Baseline default for demo user

        # Check if beneficiary is new
        beneficiary_is_new = True
        if tx.beneficiary_id:
            b_stmt = select(Beneficiary).where(Beneficiary.id == tx.beneficiary_id)
            b_res = await self.db.execute(b_stmt)
            b = b_res.scalar_one_or_none()
            if b and b.trust_level in ("known", "trusted"):
                beneficiary_is_new = False
        elif tx.beneficiary_name:
            b_stmt = select(Beneficiary).where(
                Beneficiary.user_id == user_id,
                Beneficiary.display_name == tx.beneficiary_name,
            )
            b_res = await self.db.execute(b_stmt)
            b = b_res.scalar_one_or_none()
            if b and b.trust_level in ("known", "trusted"):
                beneficiary_is_new = False

        ctx = RiskContext(
            amount=tx.amount,
            average_amount=average_amount,
            beneficiary_is_new=beneficiary_is_new,
            is_unusual_time=is_unusual_time,
            is_untrusted_device=is_untrusted_device,
        )

        decision = self.risk_engine.evaluate(ctx)

        tx.risk_score = decision.score
        tx.risk_level = decision.level.value
        tx.risk_reasons = {"reasons": decision.reasons}

        # Transition: PARSED -> RISK_ASSESSED -> AWAITING_CONFIRMATION / BLOCKED
        if decision.is_blocked:
            tx.status = TransactionStatus.BLOCKED
        else:
            tx.status = TransactionStatus.AWAITING_CONFIRMATION

        await self.audit_service.log(
            event_type="transaction.risk_assessed",
            actor_user_id=user_id,
            resource_type="transaction",
            resource_id=tx.id,
            metadata={
                "risk_score": decision.score,
                "risk_level": decision.level.value,
                "status": tx.status,
                "reasons": decision.reasons,
            },
        )
        await self.db.commit()
        await self.db.refresh(tx)

        # Trigger risk-based notification for Trusted Circle if configured
        try:
            from app.services.trusted_circle_service import TrustedCircleService
            tc_service = TrustedCircleService(self.db)
            await tc_service.generate_notifications_if_needed(tx)
        except Exception:
            pass  # Do not block transaction flow if notification fails

        return tx

    async def confirm_and_execute(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Transaction:
        """
        User-only final confirmation.

        Transitions:
        AWAITING_CONFIRMATION -> CONFIRMED -> PROCESSING -> COMPLETED (or FAILED)
        """
        tx = await self.get_transaction(transaction_id, user_id)

        current_status = TransactionStatus(tx.status)

        # Only transactions in AWAITING_CONFIRMATION can be confirmed
        if current_status != TransactionStatus.AWAITING_CONFIRMATION:
            if current_status == TransactionStatus.BLOCKED:
                raise TransactionNotConfirmableError()
            raise InvalidStateTransitionError(tx.status, TransactionStatus.CONFIRMED)

        # Transition: AWAITING_CONFIRMATION -> CONFIRMED
        tx.status = TransactionStatus.CONFIRMED
        await self.db.flush()

        await self.audit_service.log(
            event_type="transaction.confirmed",
            actor_user_id=user_id,
            resource_type="transaction",
            resource_id=tx.id,
        )

        # Transition: CONFIRMED -> PROCESSING
        tx.status = TransactionStatus.PROCESSING
        if not tx.idempotency_key:
            tx.idempotency_key = f"tx_{tx.id}_{uuid.uuid4().hex[:12]}"
        await self.db.flush()

        # Call MockBankingProvider
        result = await self.banking_provider.transfer(
            user_id=user_id,
            beneficiary_id=tx.beneficiary_id,
            amount=tx.amount,
            idempotency_key=tx.idempotency_key,
        )

        if result.success:
            tx.status = TransactionStatus.COMPLETED
            tx.bank_reference = result.reference

            # Update beneficiary last_used_at if applicable
            if tx.beneficiary_id:
                b_stmt = select(Beneficiary).where(Beneficiary.id == tx.beneficiary_id)
                b_res = await self.db.execute(b_stmt)
                b = b_res.scalar_one_or_none()
                if b:
                    from datetime import datetime, timezone
                    b.last_used_at = datetime.now(timezone.utc)
                    if b.trust_level == "new":
                        b.trust_level = "known"

            await self.audit_service.log(
                event_type="transaction.completed",
                actor_user_id=user_id,
                resource_type="transaction",
                resource_id=tx.id,
                metadata={"bank_reference": tx.bank_reference},
            )
        else:
            tx.status = TransactionStatus.FAILED
            await self.audit_service.log(
                event_type="transaction.failed",
                actor_user_id=user_id,
                resource_type="transaction",
                resource_id=tx.id,
                metadata={"error": result.error_message},
            )

        await self.db.commit()
        await self.db.refresh(tx)
        return tx
