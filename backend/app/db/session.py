"""
Database session management for PostgreSQL + pgvector.

Provides synchronous and asynchronous database engines and session factories.
"""

from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

Base = declarative_base()

# Sync Engine and SessionMaker (used for migrations and sync CLI scripts)
sync_engine = create_engine(
    settings.sync_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async Engine and SessionMaker (used for high-performance FastAPI async endpoints)
async_engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_sync_db() -> Generator[Session, None, None]:
    """Provide a synchronous transactional database session."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous transactional database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
