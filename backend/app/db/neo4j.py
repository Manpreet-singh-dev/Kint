"""
Neo4j Graph Database Driver and Session Management.

Provides driver lifecycle management and session factories for GraphRAG operations.
"""

import logging
from typing import AsyncGenerator, Generator
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession, GraphDatabase, Driver, Session

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_sync_driver: Driver | None = None
_async_driver: AsyncDriver | None = None


def get_neo4j_driver() -> Driver:
    """Get or initialize the synchronous Neo4j driver."""
    global _sync_driver
    if _sync_driver is None:
        _sync_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _sync_driver


def get_async_neo4j_driver() -> AsyncDriver:
    """Get or initialize the asynchronous Neo4j driver."""
    global _async_driver
    if _async_driver is None:
        _async_driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _async_driver


def close_neo4j_drivers() -> None:
    """Close synchronous and asynchronous Neo4j driver connections."""
    global _sync_driver, _async_driver
    if _sync_driver is not None:
        _sync_driver.close()
        _sync_driver = None
        logger.info("Closed synchronous Neo4j driver.")
    if _async_driver is not None:
        # AsyncDriver close is a coroutine or can be called synchronously in driver 5.x
        try:
            import asyncio
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(_async_driver.close())
            else:
                asyncio.run(_async_driver.close())
        except Exception as e:
            logger.warning(f"Error closing async Neo4j driver: {e}")
        _async_driver = None
        logger.info("Closed asynchronous Neo4j driver.")


def verify_neo4j_connection() -> bool:
    """
    Verify connectivity to the Neo4j instance.
    Returns True if connection succeeds, False otherwise.
    """
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        return True
    except Exception as exc:
        logger.error(f"Failed to connect to Neo4j at {settings.NEO4J_URI}: {exc}")
        return False


def get_sync_neo4j_session() -> Generator[Session, None, None]:
    """Provide a synchronous Neo4j session."""
    driver = get_neo4j_driver()
    session = driver.session(database=settings.NEO4J_DATABASE)
    try:
        yield session
    finally:
        session.close()


async def get_async_neo4j_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous Neo4j session."""
    driver = get_async_neo4j_driver()
    session = driver.session(database=settings.NEO4J_DATABASE)
    try:
        yield session
    finally:
        await session.close()
