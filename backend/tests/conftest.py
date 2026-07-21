"""
Root test configuration and shared fixtures.

Provides:
- Async test client (httpx)
- In-memory test database session
- Redis mock
- Authenticated user fixture
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from app.main import create_app
from app.dependencies.database import get_db
from app.platform.auth.dependencies import get_current_active_user, get_current_user
from app.platform.auth.models import TokenPayload
from shared.base_model import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

TEST_USER = TokenPayload(
    sub="00000000-0000-0000-0000-000000000001",
    email="test-agent@lumay.test",
    roles=["admin", "agent", "manager"],
    jti="test-jti",
    exp=datetime.now(UTC),
    iat=datetime.now(UTC),
)


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(32)"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Default test client — pre-authenticated as a logged-in employee, since
    that's how every existing endpoint call in this suite represents real
    traffic (the employee frontend always attaches a token). Use
    `unauthenticated_client` for the specific 401-without-a-token tests."""
    app = create_app()

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[get_current_active_user] = lambda: TEST_USER

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def unauthenticated_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """No auth override — exercises the real oauth2/JWT dependency chain for
    testing that protected endpoints actually reject an unauthenticated caller."""
    app = create_app()

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac