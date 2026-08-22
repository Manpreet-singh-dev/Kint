"""
Vector Store Service (Phase 3 RAG & Vector Retrieval).

Role in Pipeline:
Provides semantic storage and similarity retrieval over framework documentation,
code patterns, and generated application files.
Uses PostgreSQL + pgvector as the primary storage engine with an in-memory
vector store fallback for resilience when offline or running in testing environments.
"""

import math
from typing import Any, Dict, List, Optional
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import DocumentChunk
from app.db.session import SyncSessionLocal


class VectorSearchResult:
    """Represents a matched chunk with similarity score and metadata."""

    def __init__(
        self,
        chunk_id: int,
        collection_name: str,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        similarity_score: float,
    ):
        self.chunk_id = chunk_id
        self.collection_name = collection_name
        self.document_id = document_id
        self.content = content
        self.metadata = metadata
        self.similarity_score = similarity_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "collection_name": self.collection_name,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata,
            "similarity_score": round(self.similarity_score, 4),
        }


class VectorStoreService:
    """Service managing embedding storage and semantic search via pgvector / memory fallback."""

    def __init__(self, db_session_factory=SyncSessionLocal):
        self.db_session_factory = db_session_factory
        self.settings = get_settings()
        self._memory_chunks: List[Dict[str, Any]] = []
        self._next_memory_id = 1

    def insert_chunk(
        self,
        collection_name: str,
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Insert a single document chunk with embedding."""
        return self.insert_chunks_batch(
            collection_name=collection_name,
            chunks=[{
                "document_id": document_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
            }]
        )[0]

    def insert_chunks_batch(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]],
    ) -> List[int]:
        """
        Insert multiple document chunks into vector storage.

        Args:
            collection_name: Category or dataset name (e.g. 'framework_docs', 'app_code').
            chunks: List of dicts containing 'document_id', 'content', 'embedding', and optional 'metadata'.

        Returns:
            List of generated chunk IDs.
        """
        if not chunks:
            return []

        # Attempt to insert into PostgreSQL + pgvector
        try:
            with self.db_session_factory() as session:
                created_ids = []
                for item in chunks:
                    chunk_obj = DocumentChunk(
                        collection_name=collection_name,
                        document_id=item["document_id"],
                        content=item["content"],
                        embedding=item.get("embedding"),
                        metadata_json=item.get("metadata", {}),
                    )
                    session.add(chunk_obj)
                    session.flush()
                    created_ids.append(chunk_obj.id)
                session.commit()
                return created_ids
        except Exception:
            # Fallback to in-memory vector storage
            created_ids = []
            for item in chunks:
                chunk_id = self._next_memory_id
                self._next_memory_id += 1
                self._memory_chunks.append({
                    "id": chunk_id,
                    "collection_name": collection_name,
                    "document_id": item["document_id"],
                    "content": item["content"],
                    "embedding": item.get("embedding", []),
                    "metadata": item.get("metadata", {}),
                })
                created_ids.append(chunk_id)
            return created_ids

    def search_similar(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """
        Perform semantic similarity search using cosine distance (<=>).

        Args:
            collection_name: Target collection to search within.
            query_embedding: Vector representation of the search query.
            limit: Maximum number of chunks to return.
            score_threshold: Minimum cosine similarity score (0.0 to 1.0).

        Returns:
            List of VectorSearchResult ordered by similarity descending.
        """
        # Attempt pgvector search first
        try:
            with self.db_session_factory() as session:
                # Cosine distance in pgvector: embedding <=> query_vector
                # Cosine similarity = 1 - cosine_distance
                stmt = (
                    select(
                        DocumentChunk,
                        DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
                    )
                    .where(DocumentChunk.collection_name == collection_name)
                    .where(DocumentChunk.embedding.is_not(None))
                    .order_by("distance")
                    .limit(limit)
                )
                results = session.execute(stmt).all()
                search_results = []
                for chunk, distance in results:
                    similarity = max(0.0, 1.0 - (distance or 0.0))
                    if similarity >= score_threshold:
                        search_results.append(
                            VectorSearchResult(
                                chunk_id=chunk.id,
                                collection_name=chunk.collection_name,
                                document_id=chunk.document_id,
                                content=chunk.content,
                                metadata=chunk.metadata_json or {},
                                similarity_score=similarity,
                            )
                        )
                return search_results

        except Exception:
            # Fallback to in-memory cosine search
            return self._memory_cosine_search(
                collection_name=collection_name,
                query_embedding=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
            )

    def delete_collection(self, collection_name: str) -> int:
        """Delete all chunks belonging to a collection."""
        try:
            with self.db_session_factory() as session:
                deleted = session.query(DocumentChunk).filter(DocumentChunk.collection_name == collection_name).delete()
                session.commit()
                return deleted
        except Exception:
            initial_count = len(self._memory_chunks)
            self._memory_chunks = [c for c in self._memory_chunks if c["collection_name"] != collection_name]
            return initial_count - len(self._memory_chunks)

    def _memory_cosine_search(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int,
        score_threshold: float,
    ) -> List[VectorSearchResult]:
        """Compute cosine similarity over memory stored chunks."""
        matches = []
        for item in self._memory_chunks:
            if item["collection_name"] != collection_name or not item.get("embedding"):
                continue

            similarity = self._compute_cosine_similarity(query_embedding, item["embedding"])
            if similarity >= score_threshold:
                matches.append((item, similarity))

        matches.sort(key=lambda x: x[1], reverse=True)
        top_matches = matches[:limit]

        return [
            VectorSearchResult(
                chunk_id=item["id"],
                collection_name=item["collection_name"],
                document_id=item["document_id"],
                content=item["content"],
                metadata=item["metadata"],
                similarity_score=similarity,
            )
            for item, similarity in top_matches
        ]

    @staticmethod
    def _compute_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)
