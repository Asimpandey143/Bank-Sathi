# API Specification

Base URL:

```text
/api/v1
```

## Authentication

### POST /auth/register

Request:
```json
{
  "phone": "9999999999",
  "name": "Demo User"
}
```

### POST /auth/login

Returns a prototype JWT.

## User

### GET /users/me

Returns profile and accessibility preferences.

### PATCH /users/me/preferences

```json
{
  "language": "en",
  "font_scale": 1.5,
  "high_contrast": true,
  "speech_rate": 0.8,
  "confirmation_mode": "double"
}
```

## Intent

### POST /ai/parse-intent

Request:
```json
{
  "text": "Send 5000 rupees to Ravi"
}
```

Response:
```json
{
  "intent": "TRANSFER",
  "amount": "5000.00",
  "currency": "INR",
  "beneficiary_name": "Ravi",
  "confidence": 0.96
}
```

## Transactions

### POST /transactions/draft

Creates a transaction draft.

### POST /transactions/{id}/risk-assess

Runs deterministic risk assessment.

### POST /transactions/{id}/confirm

Requires user authorization and confirmation.

### POST /transactions/{id}/cancel

Cancels a non-final transaction.

### GET /transactions/{id}

Returns safe transaction status.

## Trusted Circle

### POST /trusted-circle/members/invite
Invite a trusted contact (daughter, son, spouse, etc.) with explicit relationship.

### GET /trusted-circle/members
List trusted circle members for the authenticated user.

### POST /trusted-circle/members/{id}/accept
Accept a pending trusted circle membership invitation.

### DELETE /trusted-circle/members/{id}
Revoke a trusted circle member.

### GET /trusted-circle/notifications
List privacy-safe risk notifications sent to the trusted circle member.

### GET /trusted-circle/notifications/{id}
Get specific privacy-safe transaction summary and flagged risk reasons.

### POST /trusted-circle/notifications/{id}/response
Submit advisory second opinion (`LOOKS_EXPECTED`, `NOT_RECOGNIZED`, `REQUEST_USER_VERIFICATION`). Advisory only — cannot execute or approve payments.

## Community

### GET /community/sessions

List sessions.

### POST /community/sessions

Create a session.

### POST /community/sessions/{id}/join

Join a session.

## Health

### GET /health

Returns:

```json
{
  "status": "ok"
}
```

## API rules

- Every protected endpoint validates JWT.
- Every resource checks ownership/authorization.
- Transaction amount is server-validated.
- Client-provided risk scores are ignored.
- Client-provided "approved" flags are ignored.
- Money values use Decimal.
- Errors use a consistent JSON format.
