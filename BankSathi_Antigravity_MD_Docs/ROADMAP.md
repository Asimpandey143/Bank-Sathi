# Implementation Roadmap

## Phase 0 — Setup

- create monorepo
- Docker Compose
- FastAPI
- PostgreSQL
- Redis
- React/TypeScript
- environment configuration

## Phase 1 — Core backend

- users
- accessibility profile
- beneficiaries
- transactions
- mock bank
- audit events

## Phase 2 — Risk engine

Implement deterministic scoring.

Acceptance:
- known normal transfer → LOW
- unusual amount → MEDIUM
- new beneficiary + unusual context → HIGH
- limit violation → CRITICAL

## Phase 3 — AI

- intent extraction
- Pydantic schema
- provider adapter
- fallback parser for demo reliability

## Phase 4 — Helper

- invitation
- temporary session
- WebSocket
- abstracted transaction view
- permission enforcement

## Phase 5 — Accessibility

- font scaling
- high contrast
- screen-reader labels
- keyboard support
- voice input
- TTS

## Phase 6 — Community

- session list
- join
- host
- participant state
- summary

## Phase 7 — Testing

- unit
- API
- security
- E2E

## Phase 8 — Demo polish

- seed demo users
- seed beneficiaries
- seed transaction history
- realistic UI
- latency indicators
- error states
- presentation script

## Future

- real banking partnerships
- formal KYC providers
- stronger fraud models
- multilingual voice
- regulated deployment
