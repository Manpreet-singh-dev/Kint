"""
Database initialization script for PostgreSQL + pgvector.

Enables the pgvector extension and creates all required schema tables.
"""

import logging
from sqlalchemy import text
from app.db.session import Base, sync_engine
from app.db.models import DocumentChunk  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> bool:
    """
    Initialize Postgres database by enabling pgvector extension and creating tables.

    Returns:
        bool: True if initialization succeeded, False otherwise.
    """
    try:
        with sync_engine.connect() as conn:
            # Enable pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            logger.info("pgvector extension verified/created successfully.")

        # Create all tables
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database schema tables created successfully.")
        return True

    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = init_db()
    if success:
        print("Database + pgvector initialized successfully.")
    else:
        print("Database initialization failed or PostgreSQL instance not reachable.")
