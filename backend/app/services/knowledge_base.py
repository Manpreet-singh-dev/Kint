"""
Knowledge Base Ingestion and Retrieval Service (Phase 3 RAG).

Role in Pipeline:
Curates, chunks, embeds, and manages framework documentation and architectural patterns
(FastAPI, Next.js, Canvas, Vanilla Web) in Postgres + pgvector for RAG augmentation.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorSearchResult, VectorStoreService


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge" / "frameworks"
FRAMEWORK_COLLECTION = "framework_patterns"


class KnowledgeBaseService:
    """Service for chunking, embedding, and querying framework knowledge patterns."""

    def __init__(
        self,
        vector_store: Optional[VectorStoreService] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.embedding_service = embedding_service or EmbeddingService()

    def seed_framework_docs(self, knowledge_dir: Optional[Path] = None) -> int:
        """
        Read all framework markdown files, chunk by sections, embed, and store in pgvector.

        Returns:
            Total number of chunks ingested.
        """
        source_dir = knowledge_dir or KNOWLEDGE_DIR
        if not source_dir.exists():
            return 0

        # Clean existing framework collection
        self.vector_store.delete_collection(FRAMEWORK_COLLECTION)

        all_chunks = []
        for file_path in source_dir.glob("*.md"):
            chunks = self._chunk_markdown_file(file_path)
            all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        # Compute embeddings in batch
        texts_to_embed = [c["content"] for c in all_chunks]
        embeddings = self.embedding_service.embed_batch(texts_to_embed)

        for chunk_data, emb in zip(all_chunks, embeddings):
            chunk_data["embedding"] = emb

        created_ids = self.vector_store.insert_chunks_batch(
            collection_name=FRAMEWORK_COLLECTION,
            chunks=all_chunks,
        )
        return len(created_ids)

    def query_patterns(
        self,
        query: str,
        limit: int = 3,
        framework: Optional[str] = None,
        score_threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """
        Retrieve relevant framework patterns given a user query or build requirement.

        Args:
            query: Natural language search query or prompt requirement.
            limit: Maximum number of chunks to return.
            framework: Optional filter (e.g. 'fastapi', 'nextjs', 'vanilla').
            score_threshold: Minimum similarity threshold.

        Returns:
            List of matching VectorSearchResult objects.
        """
        query_vector = self.embedding_service.embed_text(query)
        results = self.vector_store.search_similar(
            collection_name=FRAMEWORK_COLLECTION,
            query_embedding=query_vector,
            limit=limit * 2 if framework else limit,
            score_threshold=score_threshold,
        )

        if framework:
            filtered = [
                r for r in results
                if r.metadata.get("framework", "").lower() == framework.lower()
            ]
            return filtered[:limit]

        return results[:limit]

    def _chunk_markdown_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse markdown file into discrete section-based chunks with metadata."""
        content = file_path.read_text(encoding="utf-8")
        filename = file_path.name

        # Infer framework from filename
        framework = "general"
        if "fastapi" in filename.lower():
            framework = "fastapi"
        elif "nextjs" in filename.lower() or "react" in filename.lower():
            framework = "nextjs"
        elif "vanilla" in filename.lower() or "canvas" in filename.lower():
            framework = "vanilla_web"

        # Split on section headings (## Heading)
        sections = re.split(r"\n(?=##\s+)", content)
        chunks = []

        doc_title_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        doc_title = doc_title_match.group(1) if doc_title_match else filename

        for idx, sec in enumerate(sections):
            sec_text = sec.strip()
            if not sec_text:
                continue

            sec_title_match = re.search(r"##\s+(.+)", sec_text)
            sec_title = sec_title_match.group(1).strip() if sec_title_match else f"Section {idx + 1}"

            chunks.append({
                "document_id": f"{filename}#{idx + 1}",
                "content": sec_text,
                "metadata": {
                    "source_file": filename,
                    "framework": framework,
                    "document_title": doc_title,
                    "section_title": sec_title,
                    "chunk_index": idx,
                },
            })

        return chunks


if __name__ == "__main__":
    kb = KnowledgeBaseService()
    count = kb.seed_framework_docs()
    print(f"Ingested {count} framework pattern chunks into vector store.")
