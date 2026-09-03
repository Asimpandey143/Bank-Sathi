"""
Database session management.

Uses SQLAlchemy async engine with asyncpg driver.
Connection pool is created at startup and closed at shutdown.

NEVER use Redis as financial data source of truth (ADR-004).
PostgreSQL is the persistent source of truth.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Global engine — created in lifespan, reused across requests
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


async def create_db_pool() -> None:
    """Create the async engine and session factory on startup."""
    global _engine, _session_factory
    pool_args = {}
    if "sqlite" not in settings.database_url:
        pool_args = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
        }

    _engine = create_async_engine(
        settings.database_url,
        echo=False,
        **pool_args,
    )
    _session_factory = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Ensure tables are created if running local SQLite
    if "sqlite" in settings.database_url:
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db_pool() -> None:
    """Dispose the engine on shutdown."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession per request.

    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    if _session_factory is None:
        raise RuntimeError("Database pool is not initialized.")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
