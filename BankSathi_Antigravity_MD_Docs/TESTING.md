# Testing Strategy

## Unit tests

Test:
- risk score calculations
- risk-level mapping
- transaction state transitions
- money validation
- accessibility preference validation
- AI schema validation

## API tests

Test:
- authentication
- authorization
- transaction creation
- confirmation
- cancellation
- helper permissions
- community sessions

## Security tests

Verify that a helper cannot:
- confirm
- execute
- modify amount
- retrieve OTP
- retrieve PIN
- retrieve credentials

## AI tests

Test examples:

```text
"send 5000 to Ravi"
"send five thousand to Ravi"
"I want to pay Ravi 5k"
"transfer ₹5000 to Ravi Kumar"
```

Expected normalized intent:

```json
{
  "intent": "TRANSFER",
  "amount": "5000.00",
  "beneficiary_name": "Ravi"
}
```

## Risk tests

Case 1:
```text
usual = 1500
current = 1000
known beneficiary
trusted device
=> LOW
```

Case 2:
```text
usual = 1500
current = 5000
known beneficiary
trusted device
=> MEDIUM
```

Case 3:
```text
new beneficiary
large amount
untrusted device
=> HIGH/CRITICAL
```

## End-to-end demo test

```text
Login
 ↓
Dashboard
 ↓
Send Money
 ↓
Voice/text intent
 ↓
Risk
 ↓
Helper guidance
 ↓
User confirmation
 ↓
Mock bank
 ↓
Success
 ↓
Audit event
```

## Definition

Do not call the project demo-ready until the complete E2E flow works without manually editing the database.
