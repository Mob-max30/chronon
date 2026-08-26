from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# Graceful driver detection
_engine = None
_AsyncSessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = settings.DATABASE_URL
        if "postgresql" in db_url:
            try:
                import asyncpg  # noqa
                # Test connection or fallback
                import socket
                s = socket.socket()
                s.settimeout(0.5)
                s.connect(("127.0.0.1", 5432))
                s.close()
                _engine = create_async_engine(
                    db_url,
                    echo=settings.DEBUG,
                    future=True,
                    pool_pre_ping=True,
                )
            except Exception:
                _engine = None

        if _engine is None:
            try:
                import aiosqlite  # noqa
                _engine = create_async_engine(
                    "sqlite+aiosqlite:///chronon_dev.db",
                    echo=False,
                    future=True,
                )
            except Exception:
                _engine = None
    return _engine


def get_session_factory():
    global _AsyncSessionLocal
    eng = get_engine()
    if _AsyncSessionLocal is None and eng is not None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=eng,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


# Module-level exports for backwards-compatibility
engine = None
AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database session."""
    factory = get_session_factory()
    if factory is not None:
        async with factory() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        yield None
