# Antigravity / Coding Agent Instructions

## Mission

Implement BankSathi as a hackathon-ready, accessibility-first banking safety prototype.

Read these files before coding:
1. README.md
2. PRD.md
3. ARCHITECTURE.md
4. WORKFLOWS.md
5. SECURITY.md
6. API.md
7. DATABASE.md
8. AI_ENGINE.md
9. ACCESSIBILITY.md
10. TESTING.md

## Non-negotiable product rule

A helper can **guide**, never **control**.

Never expose:
- OTP
- PIN
- password
- full account credentials
- sensitive authentication secrets

to a helper.

Never let a helper:
- initiate a transaction
- approve a transaction
- alter transaction amount
- alter beneficiary
- enter OTP/PIN
- access raw banking credentials

Only the user can perform final confirmation.

## Coding rules

- Use Python 3.11+.
- Use FastAPI and Pydantic for backend APIs.
- Use PostgreSQL as the persistent database.
- Use Redis only for ephemeral sessions/cache.
- Use async endpoints where I/O is asynchronous.
- Use dependency injection for DB/auth/provider dependencies.
- Keep external providers behind interfaces/adapters.
- Mock external banking, KYC, notification, and voice providers.
- Never hard-code API keys.
- Use `.env.example`, never commit `.env`.
- Never log secrets or raw authentication factors.
- Use UUIDs for primary identifiers.
- Store timestamps in UTC.
- Use decimal-safe money handling.
- Validate all transaction commands server-side.
- Never trust frontend risk scores or confirmation flags.
- The server is the final authority for transaction state transitions.

## AI rules

LLM output is untrusted input.

AI may:
- parse intent
- generate explanations
- generate transaction-story wording
- generate conversational responses

AI may NOT:
- directly execute money movement
- bypass risk checks
- approve transactions
- decide authentication requirements without deterministic policy checks

All transaction execution must go through deterministic backend services.

## Development order

1. Project scaffold
2. Database models/migrations
3. Auth
4. Mock banking provider
5. Transaction state machine
6. Risk engine
7. Helper sessions
8. AI intent service
9. Accessibility UI
10. Voice adapter
11. Notifications
12. Community sessions
13. Tests
14. Docker/deployment
15. Demo seed data

## Definition of done

A feature is done only when:
- API works
- validation exists
- error cases are handled
- authorization is checked
- tests exist
- no secret data leaks
- README usage is updated
