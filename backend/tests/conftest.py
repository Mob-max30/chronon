import os
import sys
from pathlib import Path

# Add backend directory to sys.path so app can be imported
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app

# Set test environment
os.environ["ENVIRONMENT"] = "test"

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def init_test_database():
    """Create all tables before each test and drop them after."""
    fastapi_app.dependency_overrides[get_db] = override_get_db
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
