# Architecture Decision Record

## ADR-001: Modular monolith

Decision: use a modular monolith for MVP.

Reason:
- faster development
- simpler deployment
- easier debugging
- enough separation for later extraction

## ADR-002: FastAPI

Decision: Python FastAPI.

Reason:
- strong async support
- Pydantic integration
- simple API development
- fits AI/ML services

## ADR-003: PostgreSQL

Decision: PostgreSQL.

Reason:
- relational integrity
- transactions
- JSONB for flexible metadata
- mature ecosystem

## ADR-004: Redis

Decision: Redis only for ephemeral state.

Examples:
- helper session state
- WebSocket presence
- rate limiting
- short-lived cache

Never use Redis as the source of truth for financial transactions.

## ADR-005: Mock bank provider

Decision: mock banking adapter for hackathon.

Reason:
Real financial integrations require partnerships, security controls, compliance, and approved authentication flows.

## ADR-006: Deterministic risk engine

Decision: rules first.

Reason:
- explainable
- predictable
- easy to test
- safer than letting an LLM decide transaction authorization

## ADR-007: AI provider abstraction

Decision: isolate LLM/voice vendors behind interfaces.

Reason:
The team can switch providers without rewriting product logic.

## ADR-008: Trusted Circle and Second-Opinion Model (No Screen-Sharing)

Decision: Remove all screen-sharing, remote viewing, and remote control. Implement a Trusted Circle second-opinion notification model.

Reason:
- Privacy & Safety: Screen sharing risks exposing OTPs, passwords, notifications, and balance information.
- Clear Boundary: Family members provide an advisory second opinion ("Looks Expected" / "I Don't Recognize This"), while the user retains 100% final authorization control.
- Regulatory & Technical Simplicity: Avoids heavy WebRTC dependencies and remote-control security risks.
