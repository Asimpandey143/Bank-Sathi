# AI / ML Engine

## Principle

AI assists understanding; deterministic code controls money movement.

## 1. Intent extraction

Supported intents:

```text
CHECK_BALANCE
TRANSFER
PAY_BILL
LIST_TRANSACTIONS
HELP
CANCEL
UNKNOWN
```

Input:

```text
"Send five thousand to Ravi"
```

Output schema:

```json
{
  "intent": "TRANSFER",
  "amount": "5000.00",
  "currency": "INR",
  "beneficiary_name": "Ravi",
  "confidence": 0.95
}
```

If confidence is low, ask a clarification question.

## 2. LLM output validation

Use Pydantic.

Never accept free-form LLM output for transaction execution.

```text
LLM
 ↓
JSON
 ↓
Pydantic validation
 ↓
business-rule validation
 ↓
risk engine
```

## 3. Risk engine

Start with a deterministic score.

Example features:

```text
amount_deviation
beneficiary_novelty
transaction_frequency
device_trust
time_anomaly
daily_limit_remaining
```

Example policy:

```text
score < 25       LOW
25–49            MEDIUM
50–74            HIGH
>= 75            CRITICAL
```

Example:

```python
score = 0

if amount > average_amount * 2:
    score += 30

if beneficiary_is_new:
    score += 25

if unusual_time:
    score += 10

if untrusted_device:
    score += 30

if amount > daily_limit_remaining:
    score = 100
```

These thresholds are prototype policy and must be configurable.

## 4. Explainability

Return machine-readable reasons:

```json
{
  "risk_level": "MEDIUM",
  "score": 30,
  "reasons": [
    "Amount is significantly above user's recent average"
  ]
}
```

## 5. AI safety

AI must never:
- call the banking provider directly
- bypass confirmation
- lower risk level
- override transaction limits
- invent transaction success

## 6. Future ML

A later production system could use:
- Isolation Forest
- gradient boosting
- sequence-based behavior modeling
- graph-based beneficiary analysis

For the hackathon, deterministic rules + explainability are preferred.
