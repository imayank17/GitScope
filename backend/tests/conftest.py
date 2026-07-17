import asyncio
from contextlib import asynccontextmanager
import pytest
from fastapi import FastAPI
import httpx
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

# 1. Force settings to use SQLite in-memory URL before importing session
from app.core.config import settings

settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 2. Import database modules and patch session/engine
import app.database.session as db_session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Monkeypatch the engine and sessionmaker in the session module so background tasks use it
db_session.engine = test_engine
db_session.AsyncSessionLocal = TestingSessionLocal


# 3. Intercept and override the lifespan to bypass PostgreSQL-specific ALTER TABLE migrations
from app.main import app


@asynccontextmanager
async def test_lifespan(app_instance: FastAPI):
    # Set up http_client on app state
    app_instance.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    )
    yield
    await app_instance.state.http_client.aclose()


# Override lifespan context
app.router.lifespan_context = test_lifespan


# Session-wide autouse fixture to guarantee app.state.http_client is populated
@pytest.fixture(scope="session", autouse=True)
async def setup_app_state_client():
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    )
    yield
    await app.state.http_client.aclose()


# 4. Standard anyio backend fixture for pytest-asyncio compatibility
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# 5. Database lifecycle fixture - ensures clean tables per test
@pytest.fixture(autouse=True)
async def init_db():
    from app.database.base import Base
    import app.models  # Ensure all models are registered with Base.metadata

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 6. Database session fixture for direct DB operations in tests
@pytest.fixture
async def db():
    async with TestingSessionLocal() as session:
        yield session


# 7. Dependency override for FastAPI get_db dependency
@pytest.fixture(autouse=True)
def override_db(db):
    from app.database.session import get_db

    async def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


# 8. HTTP Client Fixtures


@pytest.fixture
async def client():
    """Async Client for testing endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def sync_client():
    """Sync TestClient for testing endpoints where async context isn't required."""
    with TestClient(app) as tc:
        yield tc
