# BankSathi

**Accessibility-first digital banking companion.**

> Shared guidance, not shared access.

A hackathon prototype demonstrating a safer interaction model for accessible digital banking. Elderly users and people with disabilities can perform banking via voice or text, with AI assistance and trusted helper guidance — without giving the helper any account control.

---

## Quick Start

### Prerequisites

- Docker Desktop
- Docker Compose

### Run

```bash
# 1. Clone
git clone <repo-url>
cd banksaathi

# 2. Set up environment
cp .env.example .env
# Edit .env if needed (defaults work for local dev)

# 3. Start all services
docker compose up

# 4. Access
#    Frontend:  http://localhost:5173
#    Backend:   http://localhost:8000
#    API docs:  http://localhost:8000/docs
#    Health:    http://localhost:8000/health
```

### Run tests (backend)

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app tests/
```

---

## Demo scenario

An elderly user (Meena) wants to send ₹5,000 to Ravi.

1. Voice input: *"Send five thousand rupees to Ravi."*
2. AI extracts: `TRANSFER | ₹5,000 | Ravi Kumar`
3. Risk engine: **MEDIUM** — amount higher than usual
4. Helper guidance: helper sees intent + risk, cannot approve
5. Transaction story shown to user
6. **User-only** final confirmation
7. Mock bank executes transfer
8. Audit trail recorded

---

## Architecture

```
Frontend (React + TypeScript)
         │
         │ HTTPS / WebSocket
         ▼
 FastAPI (modular monolith)
         │
 ┌───────┼──────────────┐
 ▼       ▼              ▼
Transaction  AI/Conversation  Helper/Session
 Service      Service          Service
     │             │                │
 Risk Engine   LLM Provider    Redis/WebSocket
     │
 Mock Banking Provider
     │
 PostgreSQL
```

## Safety guarantees

| Actor | Can See | Cannot See | Cannot Do |
|-------|---------|------------|-----------|
| Helper | Intent, amount, risk, guidance | OTP, PIN, credentials | Approve, execute, modify |
| AI | Natural language input | Banking credentials | Execute transactions, bypass risk |
| Backend | Everything | — | Trust frontend risk scores |
| Frontend | Transaction status | Backend secrets | Override server risk/state |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL 15 |
| Cache | Redis 7 (ephemeral only) |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Auth | JWT (prototype) |
| AI | Provider abstraction (mock default) |
| Frontend | React 18 + TypeScript + Vite |
| Containers | Docker Compose |

---

## Important disclaimer

This is a **hackathon prototype**, not a production banking system.

- No real bank/UPI integration
- No real Aadhaar/KYC
- Mock authentication only
- Not RBI-approved

> "This prototype demonstrates a safer interaction model for accessible digital banking."
