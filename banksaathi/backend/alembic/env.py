"""
Alembic migrations environment.

Uses async SQLAlchemy engine (asyncpg driver).
Reads DATABASE_URL from environment variables.
"""
import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# -- Alembic Config object ------------------------------------------------
config = context.config

# Override sqlalchemy.url from DATABASE_URL env var (docker-compose sets this)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -- Import all models so Alembic sees them --------------------------------
# This import must happen AFTER Base is defined in app.database
from app.database import Base  # noqa: E402

# Import all models for Alembic autogenerate
from app.models import (  # noqa: F401
    User,
    AccessibilityProfile,
    Beneficiary,
    Transaction,
    HelperAssignment,
    HelperSession,
    CommunitySession,
    AuditEvent,
)

target_metadata = Base.metadata


# --------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
