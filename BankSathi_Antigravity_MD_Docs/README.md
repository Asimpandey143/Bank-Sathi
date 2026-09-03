# BankSathi

BankSathi is an accessibility-first digital banking companion for elderly users and people with visual, hearing, motor, or cognitive disabilities.

## Core idea

BankSathi does **not** give a helper control over a user's bank account.

The core safety principle is:

> **Shared guidance, not shared access.**

A user can perform banking through a simplified accessible interface or voice. A trusted helper can guide the user through a temporary session, but the helper cannot enter OTP/PIN, approve a transaction, modify the user's bank account, or see secrets.

## MVP

Build a working hackathon prototype around these flows:

1. User registration/login.
2. Accessibility profile.
3. Mock bank account and transaction history.
4. Send-money flow using voice or text.
5. AI intent extraction into structured JSON.
6. Risk engine based on amount, beneficiary history, frequency, and device trust.
7. Adaptive confirmation: LOW / MEDIUM / HIGH / CRITICAL.
8. Helper session with an abstracted view.
9. AI voice companion when no helper is available.
10. Transaction story / simplified confirmation.
11. Mock transaction execution.
12. Audit log and notifications.
13. Community learning-session prototype.

## Important prototype boundary

This repository must use a **mock banking provider**. Never attempt to implement real UPI, bank credentials, OTP collection, Aadhaar storage, or production KYC inside the hackathon MVP.

The original concept includes verified helpers, voice assistance, transaction stories, fraud detection, and community sessions. These are the product pillars described in the supplied concept document. [Source: supplied BankSathi report]

## Suggested stack

- Backend: Python + FastAPI
- Database: PostgreSQL
- Cache/session state: Redis
- ORM: SQLAlchemy
- Validation: Pydantic
- AI: LLM API behind a provider abstraction
- Voice: browser/mobile speech recognition + TTS provider abstraction
- User frontend: React/TypeScript or Flutter
- Helper frontend: React/TypeScript
- Real-time: WebSocket
- Auth: JWT for prototype
- Containers: Docker Compose

## Build philosophy

Prefer a modular monolith over premature microservices.

The code must be:
- easy to run locally
- deterministic when AI is unavailable
- safe by default
- testable
- strongly typed at API boundaries
- documented
