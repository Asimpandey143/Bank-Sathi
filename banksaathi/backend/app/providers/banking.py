"""
Banking Provider Abstraction & Mock Implementation

Architecture: Provider pattern (ADR-005)
Mock provider simulates balance, transfers, idempotency, and reference generation.
Never connects to real financial systems.
"""
from dataclasses import dataclass
from decimal import Decimal
import random
from typing import Protocol
import uuid


@dataclass
class TransferResult:
    success: bool
    reference: str | None = None
    error_message: str | None = None


class BankingProvider(Protocol):
    async def get_balance(self, user_id: uuid.UUID) -> Decimal:
        """Get the current available balance for a user."""
        ...

    async def transfer(
        self,
        user_id: uuid.UUID,
        beneficiary_id: uuid.UUID | None,
        amount: Decimal,
        idempotency_key: str,
    ) -> TransferResult:
        """Execute a transfer against the mock bank."""
        ...


class MockBankingProvider:
    """
    In-memory mock banking provider for hackathon prototype.
    Simulates:
    - User account balances (defaults to 50,000.00 INR)
    - Transfers with reference generation
    - Idempotency via key storage
    - Balance deduction on successful transfer
    - Insufficient funds failure simulation
    """

    def __init__(self, default_balance: Decimal = Decimal("50000.00")) -> None:
        self.default_balance = default_balance
        self._balances: dict[uuid.UUID, Decimal] = {}
        # idempotency_key -> TransferResult
        self._processed_transfers: dict[str, TransferResult] = {}

    async def get_balance(self, user_id: uuid.UUID) -> Decimal:
        if user_id not in self._balances:
            self._balances[user_id] = self.default_balance
        return self._balances[user_id]

    async def set_balance(self, user_id: uuid.UUID, balance: Decimal) -> None:
        self._balances[user_id] = balance

    async def transfer(
        self,
        user_id: uuid.UUID,
        beneficiary_id: uuid.UUID | None,
        amount: Decimal,
        idempotency_key: str,
    ) -> TransferResult:
        # Idempotency check: if already processed, return existing result
        if idempotency_key in self._processed_transfers:
            return self._processed_transfers[idempotency_key]

        current_balance = await self.get_balance(user_id)

        # Simulation failure: Insufficient funds
        if amount > current_balance:
            result = TransferResult(
                success=False,
                reference=None,
                error_message=f"Insufficient funds. Current balance is INR {current_balance}.",
            )
            self._processed_transfers[idempotency_key] = result
            return result

        # Deduct balance
        self._balances[user_id] = current_balance - amount

        # Generate mock bank reference, e.g. DEMO-847291
        ref_num = random.randint(100000, 999999)
        ref = f"DEMO-{ref_num}"

        result = TransferResult(
            success=True,
            reference=ref,
            error_message=None,
        )
        self._processed_transfers[idempotency_key] = result
        return result


# Singleton instance for dependency injection
_mock_banking_provider_instance = MockBankingProvider()


def get_banking_provider() -> BankingProvider:
    return _mock_banking_provider_instance
