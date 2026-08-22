"""Tests for AppIndexerService (Phase 3 RAG & Codebase Embedding)."""

import pytest
from app.services.app_indexer import AppIndexerService
from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStoreService


def test_app_indexer_chunk_html():
    """Test HTML files are split across major structural tags."""
    indexer = AppIndexerService()
    html = """<!DOCTYPE html>
<html>
<head><title>Stopwatch</title></head>
<body>
<main class="container"><h1>Timer</h1></main>
<script src="script.js"></script>
</body>
</html>"""
    chunks = indexer._chunk_file(
        filename="index.html",
        content=html,
        app_id="app_123",
        prompt="Build a stopwatch",
        extra_metadata={},
    )

    assert len(chunks) >= 2
    assert all(c["metadata"]["app_id"] == "app_123" for c in chunks)
    assert all(c["metadata"]["file_name"] == "index.html" for c in chunks)


def test_app_indexer_chunk_javascript():
    """Test JavaScript files are chunked along function boundaries."""
    indexer = AppIndexerService()
    js = """
function startTimer() {
  console.log("Timer started");
}

function pauseTimer() {
  console.log("Timer paused");
}
"""
    chunks = indexer._chunk_file(
        filename="script.js",
        content=js,
        app_id="app_123",
        prompt="Build a stopwatch",
        extra_metadata={},
    )

    assert len(chunks) >= 2
    assert any("startTimer" in c["metadata"].get("section_name", "") for c in chunks)
    assert any("pauseTimer" in c["metadata"].get("section_name", "") for c in chunks)


def test_app_indexer_index_and_query_app():
    """Test end-to-end codebase indexing and semantic search scoped by app_id."""
    vector_store = VectorStoreService()
    embedder = EmbeddingService(dimension=512)
    indexer = AppIndexerService(vector_store=vector_store, embedding_service=embedder)

    files_app_a = {
        "index.html": "<!DOCTYPE html><html><body><canvas id='snake'></canvas></body></html>",
        "script.js": "function renderSnake() { ctx.fillRect(x, y, 10, 10); }",
    }
    files_app_b = {
        "index.html": "<!DOCTYPE html><html><body><h1>Expense Tracker</h1></body></html>",
        "script.js": "function calculateNetBalance() { return income - expense; }",
    }

    app_a_id = indexer.index_generated_app(files=files_app_a, prompt="Build snake game", app_id="snake_app_01")
    app_b_id = indexer.index_generated_app(files=files_app_b, prompt="Build expense tracker", app_id="expense_app_02")

    assert app_a_id == "snake_app_01"
    assert app_b_id == "expense_app_02"

    # Query for snake rendering in App A
    results_a = indexer.query_app_code(app_id="snake_app_01", query="snake canvas render", limit=3)
    assert len(results_a) > 0
    assert all(r.metadata.get("app_id") == "snake_app_01" for r in results_a)
    assert any("renderSnake" in r.content for r in results_a)

    # Query for balance in App B
    results_b = indexer.query_app_code(app_id="expense_app_02", query="calculate balance", limit=3)
    assert len(results_b) > 0
    assert all(r.metadata.get("app_id") == "expense_app_02" for r in results_b)
    assert any("calculateNetBalance" in r.content for r in results_b)
