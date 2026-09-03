# Security Design

## Security principle

The user owns the transaction authority.

## Shared guidance, not shared access

Trusted Circle Member (e.g. Daughter, Son, Spouse):
- can receive selected risk notifications (MEDIUM / HIGH)
- can view privacy-safe transaction summary (amount, recipient, risk reasons)
- can provide advisory second opinion ("Looks Expected" / "I Don't Recognize This")
- can request user verification

Trusted Circle Member CANNOT:
- approve transactions
- execute transactions
- modify amounts or beneficiaries
- enter or view OTP
- enter or view UPI PIN / passwords
- view full bank accounts or credentials
- remotely control the user's device
- engage in screen-sharing (strictly prohibited)

Only the authenticated user can authorize money movement.

## Authentication

Prototype:
- phone + OTP simulation
- JWT access token

Production:
- use bank/provider-approved authentication
- hardware/device binding where appropriate
- secure session management

## Authorization

Every transaction operation checks:

```text
authenticated?
    ↓
resource belongs to user?
    ↓
transaction state allows action?
    ↓
risk policy satisfied?
    ↓
user confirmation present?
    ↓
execute
```

## Secrets

Use environment variables:

```text
DATABASE_URL=
REDIS_URL=
JWT_SECRET=
LLM_API_KEY=
VOICE_API_KEY=
```

Never commit `.env`.

## Logging

Safe:

```text
transaction_id=...
risk_level=MEDIUM
status=COMPLETED
```

Unsafe:

```text
otp=123456
pin=1234
password=...
full_bank_account=...
```

## Threats

### Malicious helper
Mitigation:
- least privilege
- temporary sessions
- user-only confirmation
- audit logs

### Prompt injection
Mitigation:
- structured AI outputs
- strict schemas
- deterministic transaction policy

### Replay attack
Mitigation:
- expiring session tokens
- idempotency keys
- transaction state machine

### Double transaction
Mitigation:
- idempotency key
- unique provider reference
- atomic state transitions

### Frontend tampering
Mitigation:
- server-side validation
- server-side risk calculation
- server-side authorization

## Prototype disclaimer

This is a hackathon prototype, not a production banking system.
