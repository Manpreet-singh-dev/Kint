"""Tests for VectorStoreService and DocumentChunk models (Phase 3 Postgres + pgvector)."""

import pytest
from app.db.models import DocumentChunk
from app.services.vector_store import VectorSearchResult, VectorStoreService


def test_document_chunk_model_serialization():
    """Test DocumentChunk model creation and to_dict representation."""
    chunk = DocumentChunk(
        id=10,
        collection_name="framework_docs",
        document_id="fastapi_intro.md",
        content="FastAPI is a modern, fast web framework for building APIs with Python.",
        metadata_json={"framework": "fastapi", "topic": "intro"},
        embedding=[0.1, 0.2, 0.3],
    )
    data = chunk.to_dict()

    assert data["id"] == 10
    assert data["collection_name"] == "framework_docs"
    assert data["document_id"] == "fastapi_intro.md"
    assert "FastAPI is a modern" in data["content"]
    assert data["metadata"]["framework"] == "fastapi"


def test_vector_store_batch_insert_and_cosine_search():
    """Test inserting chunks and retrieving them ranked by cosine similarity."""
    store = VectorStoreService()

    # Seed chunks with known mock vectors
    chunks = [
        {
            "document_id": "fastapi_routes.md",
            "content": "FastAPI APIRouter and dependency injection patterns.",
            "embedding": [1.0, 0.0, 0.0],  # Aligns with [1.0, 0.0, 0.0]
            "metadata": {"framework": "fastapi"},
        },
        {
            "document_id": "nextjs_app_router.md",
            "content": "Next.js App Router and React Server Components.",
            "embedding": [0.0, 1.0, 0.0],  # Orthogonal
            "metadata": {"framework": "nextjs"},
        },
        {
            "document_id": "fastapi_auth.md",
            "content": "OAuth2 and JWT authentication in FastAPI.",
            "embedding": [0.9, 0.1, 0.0],  # Close to [1.0, 0.0, 0.0]
            "metadata": {"framework": "fastapi"},
        },
    ]

    created_ids = store.insert_chunks_batch(collection_name="framework_docs", chunks=chunks)
    assert len(created_ids) == 3

    # Query vector close to FastAPI
    query_vector = [1.0, 0.0, 0.0]
    results = store.search_similar(
        collection_name="framework_docs",
        query_embedding=query_vector,
        limit=2,
    )

    assert len(results) == 2
    assert results[0].document_id == "fastapi_routes.md"
    assert results[0].similarity_score == 1.0
    assert results[1].document_id == "fastapi_auth.md"
    assert results[1].similarity_score > 0.9


def test_vector_store_score_threshold_filtering():
    """Test that search_similar honors score_threshold cutoff."""
    store = VectorStoreService()
    store.insert_chunks_batch(
        collection_name="patterns",
        chunks=[
            {"document_id": "a.md", "content": "A", "embedding": [1.0, 0.0]},
            {"document_id": "b.md", "content": "B", "embedding": [0.0, 1.0]},
        ],
    )

    # Search with high threshold
    results = store.search_similar(
        collection_name="patterns",
        query_embedding=[1.0, 0.0],
        score_threshold=0.8,
    )

    assert len(results) == 1
    assert results[0].document_id == "a.md"


def test_vector_store_delete_collection():
    """Test deleting an entire collection from vector store."""
    store = VectorStoreService()
    store.insert_chunk(
        collection_name="temp_collection",
        document_id="temp.md",
        content="Temporary content",
        embedding=[0.5, 0.5],
    )

    deleted_count = store.delete_collection("temp_collection")
    assert deleted_count >= 1

    results = store.search_similar("temp_collection", query_embedding=[0.5, 0.5])
    assert len(results) == 0


def test_vector_store_cosine_math_edge_cases():
    """Test cosine similarity computation with zero vectors and dimension mismatches."""
    assert VectorStoreService._compute_cosine_similarity([], [1.0, 2.0]) == 0.0
    assert VectorStoreService._compute_cosine_similarity([1.0], [1.0, 2.0]) == 0.0
    assert VectorStoreService._compute_cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
    assert pytest.approx(VectorStoreService._compute_cosine_similarity([1.0, 0.0], [1.0, 0.0])) == 1.0
