# System Architecture

## 1. Architecture style

Use a **modular monolith** for the hackathon.

This gives the team microservice-like separation without operational complexity.

```text
                    +----------------------+
                    |   User Mobile/Web    |
                    +----------+-----------+
                               |
                               | HTTPS / WebSocket
                               v
                    +----------------------+
                    |      FastAPI API      |
                    +----------+-----------+
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
 +----------------+   +----------------+   +----------------+
 | Transaction     |   | AI/Conversation |   | Trusted Circle |
 | Service         |   | Service        |   | Service        |
 +-------+---------+   +-------+--------+   +-------+--------+
         |                     |                    |
         v                     v                    v
 +----------------+   +----------------+   +----------------+
 | Risk Engine     |   | LLM Provider   |   | Notifications  |
 +-------+---------+   +----------------+   | (Advisory Only)|
         |                                  +----------------+
         v
 +----------------+
 | Mock Bank      |
 | Provider       |
 +-------+--------+
         |
         v
 +----------------+
 | PostgreSQL     |
 +----------------+
```

## 2. Major modules

### API
Routes, authentication, request/response models.

### User
Profiles, accessibility preferences, beneficiaries.

### Transaction
Transaction state machine and orchestration.

### Risk
Deterministic risk scoring and verification policy triggers.

### AI
Intent extraction and safe conversational responses.

### Trusted Circle
Member management, risk-based privacy-safe notifications, and advisory second opinions. Zero screen-sharing.

### Banking
Mock provider adapter.

### Community
Session scheduling and participation.

### Notifications
Risk-based alerts and advisory updates for Trusted Circle members.

### Audit
Security-sensitive event history.

## 3. Transaction state machine

```text
DRAFT
  |
  v
PARSED
  |
  v
RISK_ASSESSED
  |
  +----> BLOCKED
  |
  v
AWAITING_CONFIRMATION
  |
  +----> CANCELLED
  |
  v
CONFIRMED
  |
  v
PROCESSING
  |
  +----> FAILED
  |
  v
COMPLETED
```

The backend must reject invalid transitions.

## 4. Request path

```text
User input
   |
   v
API
   |
   v
Intent parser
   |
   v
Structured transaction command
   |
   v
Deterministic validation
   |
   v
Risk engine
   |
   v
Confirmation policy
   |
   v
User confirmation
   |
   v
Mock bank provider
   |
   v
Audit + notification
```

## 5. Deployment

For hackathon:

```text
Docker Compose
├── frontend
├── backend
├── postgres
└── redis
```

Optional:
- reverse proxy
- cloud object storage
- managed PostgreSQL
