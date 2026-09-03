"""
BankSathi — FastAPI Application Entry Point

Architecture: Modular monolith
Safety: Helper guidance, never helper control.
AI: Intent parsing only — never direct execution.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.errors import (
    BankSathiError,
    banksathi_error_handler,
    generic_error_handler,
    http_exception_handler,
)
from app.database import create_db_pool, close_db_pool

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — connect DB/Redis on startup, close on shutdown."""
    await create_db_pool()
    yield
    await close_db_pool()


app = FastAPI(
    title="BankSathi API",
    description=(
        "Accessibility-first banking safety companion. "
        "Shared guidance, not shared access."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
app.add_exception_handler(BankSathiError, banksathi_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_error_handler)

# ── Routers ─────────────────────────────────────────────────────────────────
from app.api import health  # noqa: E402
from app.api import auth, users, transactions, ai, trusted_circle, voice, community  # noqa: E402

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(trusted_circle.router, prefix="/api/v1")
app.include_router(voice.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")
