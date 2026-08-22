"""
App Indexer Service (Phase 3 RAG & Codebase Embedding).

Role in Pipeline:
Embeds the files of freshly generated applications upon successful build.
Chunks HTML, CSS, and JavaScript source code into semantic blocks, computes
dense vector embeddings, and persists them into PostgreSQL + pgvector.
Enables grounded Q&A ("Chat about this app") and code-understanding queries.
"""

import re
import uuid
from typing import Any, Dict, List, Optional

from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorSearchResult, VectorStoreService


APP_CODE_COLLECTION = "app_code"


class AppIndexerService:
    """Service responsible for chunking, embedding, and querying generated application codebases."""

    def __init__(
        self,
        vector_store: Optional[VectorStoreService] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.embedding_service = embedding_service or EmbeddingService()

    def index_generated_app(
        self,
        files: Dict[str, str],
        prompt: str,
        app_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Chunk and embed all files in a freshly generated application codebase.

        Args:
            files: Dictionary mapping filenames to file contents.
            prompt: User's original prompt used to build the app.
            app_id: Unique identifier for the app (generated if None).
            metadata: Additional metadata to attach to chunks.

        Returns:
            app_id: Unique identifier associated with the indexed codebase chunks.
        """
        resolved_app_id = app_id or f"app_{uuid.uuid4().hex[:10]}"
        if not files:
            return resolved_app_id

        all_chunks = []
        for filename, content in files.items():
            file_chunks = self._chunk_file(
                filename=filename,
                content=content,
                app_id=resolved_app_id,
                prompt=prompt,
                extra_metadata=metadata or {},
            )
            all_chunks.extend(file_chunks)

        if not all_chunks:
            return resolved_app_id

        # Compute embeddings in batch
        texts_to_embed = [c["content"] for c in all_chunks]
        embeddings = self.embedding_service.embed_batch(texts_to_embed)

        for chunk_data, emb in zip(all_chunks, embeddings):
            chunk_data["embedding"] = emb

        self.vector_store.insert_chunks_batch(
            collection_name=APP_CODE_COLLECTION,
            chunks=all_chunks,
        )

        return resolved_app_id

    def query_app_code(
        self,
        app_id: str,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """
        Perform semantic search across an indexed application codebase.

        Args:
            app_id: Target application identifier.
            query: Question or code search query.
            limit: Maximum number of relevant code chunks to return.
            score_threshold: Minimum similarity score.

        Returns:
            List of matching VectorSearchResult objects.
        """
        query_vector = self.embedding_service.embed_text(query)
        results = self.vector_store.search_similar(
            collection_name=APP_CODE_COLLECTION,
            query_embedding=query_vector,
            limit=limit * 3,  # Fetch wider set for app_id filtering
            score_threshold=score_threshold,
        )

        # Filter strictly by app_id
        filtered = [
            r for r in results
            if r.metadata.get("app_id") == app_id
        ]
        return filtered[:limit]

    def _chunk_file(
        self,
        filename: str,
        content: str,
        app_id: str,
        prompt: str,
        extra_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Chunk code files intelligently based on file type."""
        chunks = []
        ext = filename.split(".")[-1].lower() if "." in filename else ""

        if ext == "html":
            chunks.extend(self._chunk_html(filename, content))
        elif ext in ("js", "ts"):
            chunks.extend(self._chunk_javascript(filename, content))
        elif ext == "css":
            chunks.extend(self._chunk_css(filename, content))
        else:
            # General fallback chunking (paragraphs/lines)
            chunks.extend(self._chunk_general(filename, content))

        # Attach standard metadata
        for idx, item in enumerate(chunks):
            item["document_id"] = f"{app_id}:{filename}:{idx}"
            item["metadata"].update({
                "app_id": app_id,
                "file_name": filename,
                "file_type": ext,
                "prompt": prompt,
                "chunk_index": idx,
                **extra_metadata,
            })

        return chunks

    def _chunk_html(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """Chunk HTML by major structure tags (<head>, <header>, <main>, <section>, <script>)."""
        chunks = []
        # Split on top-level semantic tags
        split_pattern = r"(?=<head\b|<body\b|<header\b|<main\b|<section\b|<nav\b|<footer\b|<script\b)"
        parts = [p.strip() for p in re.split(split_pattern, content, flags=re.IGNORECASE) if p.strip()]

        if not parts:
            parts = [content]

        for p in parts:
            tag_match = re.match(r"<([a-zA-Z0-9]+)", p)
            tag_name = tag_match.group(1) if tag_match else "html_block"
            chunks.append({
                "content": p,
                "metadata": {"section_name": tag_name, "chunk_type": "html_element"},
            })
        return chunks

    def _chunk_javascript(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """Chunk JavaScript by function / class / class method declarations."""
        chunks = []
        # Split on function/class boundaries
        func_pattern = r"(?=(?:function\s+\w+|class\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>))"
        parts = [p.strip() for p in re.split(func_pattern, content) if p.strip()]

        if not parts or len(parts) == 1:
            # If no clear function boundary split, chunk by ~40 lines
            lines = content.splitlines()
            stride = 40
            for i in range(0, len(lines), stride):
                block = "\n".join(lines[i:i + stride])
                if block.strip():
                    chunks.append({
                        "content": block,
                        "metadata": {"section_name": f"lines_{i+1}_{min(i+stride, len(lines))}", "chunk_type": "js_block"},
                    })
            return chunks

        for p in parts:
            name_match = re.search(r"(?:function|class|const)\s+([a-zA-Z0-9_$]+)", p)
            symbol_name = name_match.group(1) if name_match else "anonymous_js"
            chunks.append({
                "content": p,
                "metadata": {"section_name": symbol_name, "chunk_type": "js_function"},
            })
        return chunks

    def _chunk_css(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """Chunk CSS by rules or selector blocks."""
        chunks = []
        # Split by CSS comment blocks or rule clusters
        rules = [r.strip() for r in re.split(r"(?=\/\*|\n(?=[.#a-zA-Z0-9_-]+\s*\{))", content) if r.strip()]

        if not rules or len(rules) == 1:
            chunks.append({"content": content, "metadata": {"section_name": "styles", "chunk_type": "css_all"}})
            return chunks

        # Group rules into chunks of 3-5 rules
        current_chunk = []
        for rule in rules:
            current_chunk.append(rule)
            if len(current_chunk) >= 4:
                block = "\n\n".join(current_chunk)
                chunks.append({"content": block, "metadata": {"section_name": "css_rules", "chunk_type": "css_block"}})
                current_chunk = []

        if current_chunk:
            chunks.append({"content": "\n\n".join(current_chunk), "metadata": {"section_name": "css_rules", "chunk_type": "css_block"}})

        return chunks

    def _chunk_general(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """Fallback chunker for other file extensions."""
        return [{"content": content, "metadata": {"section_name": "whole_file", "chunk_type": "generic"}}]
