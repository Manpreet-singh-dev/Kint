"""
SQLAlchemy ORM models for PostgreSQL + pgvector vector storage.

Defines the DocumentChunk table used to store chunked documentation,
framework patterns, and generated application source code with pgvector embeddings.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.session import Base

settings = get_settings()


class DocumentChunk(Base):
    """
    Table storing textual chunks with vector embeddings for semantic retrieval.
    """
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    collection_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    document_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk model to dictionary representation."""
        return {
            "id": self.id,
            "collection_name": self.collection_name,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
