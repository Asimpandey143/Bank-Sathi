"""
Test configuration and fixtures for BankSathi backend.

Uses an in-memory SQLite database for unit tests to avoid
requiring a running PostgreSQL instance.

The app lifespan (which connects to real PostgreSQL/Redis) is bypassed
in tests using dependency overrides.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app as fastapi_app

# In-memory SQLite for fast unit/API tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a fresh async engine per test function."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """Provide a clean DB session per test."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    HTTP test client with:
    - DB dependency overridden to use in-memory SQLite
    - App lifespan bypassed (no real PostgreSQL/Redis needed)
    """

    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Use lifespan=False to skip the real DB pool creation
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
