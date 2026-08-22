"""Tests for EmbeddingService and KnowledgeBaseService (Phase 3 RAG)."""

import pytest
from pathlib import Path
from app.services.embedding import EmbeddingService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.vector_store import VectorStoreService


def test_embedding_service_dimension_and_determinism():
    """Test embedding service produces vectors of correct dimension consistently."""
    embedder = EmbeddingService(dimension=1536)
    vec1 = embedder.embed_text("FastAPI dependency injection pattern")
    vec2 = embedder.embed_text("FastAPI dependency injection pattern")
    vec3 = embedder.embed_text("Next.js App Router server components")

    assert len(vec1) == 1536
    assert vec1 == vec2  # Deterministic consistency
    assert vec1 != vec3  # Distinct text yields distinct vectors


def test_embedding_service_batch():
    """Test batch embedding generation."""
    embedder = EmbeddingService(dimension=512)
    texts = ["React useState hook", "Canvas game loop", "Postgres vector query"]
    vectors = embedder.embed_batch(texts)

    assert len(vectors) == 3
    assert all(len(v) == 512 for v in vectors)


def test_knowledge_base_chunking_and_seeding(tmp_path: Path):
    """Test markdown chunking and ingestion into vector store."""
    sample_md = """# Sample Framework Docs

## Dependency Injection
Use Depends() to inject dependencies.

## Error Handling
Use custom exception handlers for structured errors.
"""
    doc_file = tmp_path / "fastapi_sample.md"
    doc_file.write_text(sample_md, encoding="utf-8")

    vector_store = VectorStoreService()
    kb = KnowledgeBaseService(vector_store=vector_store)

    chunks_count = kb.seed_framework_docs(knowledge_dir=tmp_path)
    assert chunks_count >= 2

    # Query for dependency injection
    results = kb.query_patterns("How to inject dependencies", limit=2)
    assert len(results) > 0
    assert any("Dependency Injection" in r.metadata.get("section_title", "") for r in results)


def test_knowledge_base_framework_filtering(tmp_path: Path):
    """Test querying with specific framework filter."""
    (tmp_path / "fastapi_test.md").write_text("## Fast API Routes\nFastAPI routing.", encoding="utf-8")
    (tmp_path / "nextjs_test.md").write_text("## Next.js Components\nNext.js client.", encoding="utf-8")

    vector_store = VectorStoreService()
    kb = KnowledgeBaseService(vector_store=vector_store)
    kb.seed_framework_docs(knowledge_dir=tmp_path)

    fastapi_results = kb.query_patterns("routing", framework="fastapi", limit=5)
    for r in fastapi_results:
        assert r.metadata.get("framework") == "fastapi"
