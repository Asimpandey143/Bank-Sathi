# Backend Implementation

## Directory

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── transactions.py
│   │   ├── helpers.py
│   │   ├── community.py
│   │   └── ai.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── transaction_service.py
│   │   ├── risk_engine.py
│   │   ├── intent_service.py
│   │   ├── helper_service.py
│   │   └── notification_service.py
│   ├── providers/
│   │   ├── banking.py
│   │   ├── llm.py
│   │   └── voice.py
│   └── core/
│       ├── auth.py
│       ├── security.py
│       └── errors.py
├── tests/
├── alembic/
└── requirements.txt
```

## Service responsibilities

### TransactionService

Responsible for:
- creating drafts
- validating state
- calling risk engine
- requiring confirmation
- calling bank provider
- writing audit events

### RiskEngine

Pure business logic.

Input:
```python
RiskContext(...)
```

Output:
```python
RiskDecision(
    score=30,
    level="MEDIUM",
    reasons=[...]
)
```

### BankingProvider

Interface:

```python
class BankingProvider(Protocol):
    async def get_balance(self, user_id: UUID) -> Decimal: ...
    async def transfer(
        self,
        user_id: UUID,
        beneficiary_id: UUID,
        amount: Decimal,
        idempotency_key: str,
    ) -> TransferResult: ...
```

Implement:

```text
MockBankingProvider
```

first.

## Error handling

Use structured errors:

```json
{
  "code": "TRANSACTION_NOT_CONFIRMABLE",
  "message": "Additional verification is required."
}
```

Do not expose internal stack traces.
