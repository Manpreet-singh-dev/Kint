"""
Dependency injection providers for FastAPI endpoints.

Follows the Dependency Injection pattern from the Auth0 FastAPI best practices guide.
"""

from fastapi import Depends
from app.core.config import Settings, get_settings
from app.services.coder import CoderService
from app.services.debugger import DebuggerService
from app.services.orchestrator import OrchestratorService
from app.services.planner import PlannerService
from app.services.sandbox import SandboxService
from app.services.providers import LLMProvider, get_llm_provider


from app.services.embedding import EmbeddingService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.vector_store import VectorStoreService


def get_app_settings() -> Settings:
    """Provide application settings instance."""
    return get_settings()


def get_provider(settings: Settings = Depends(get_app_settings)) -> LLMProvider:
    """Provide the configured LLM provider (Claude, Gemini, Grok, Groq)."""
    return get_llm_provider(settings)


def get_vector_store_service() -> VectorStoreService:
    """Provide VectorStoreService singleton instance."""
    return VectorStoreService()


def get_embedding_service() -> EmbeddingService:
    """Provide EmbeddingService instance."""
    return EmbeddingService()


def get_knowledge_base_service(
    vector_store: VectorStoreService = Depends(get_vector_store_service),
    embedding: EmbeddingService = Depends(get_embedding_service),
) -> KnowledgeBaseService:
    """Provide KnowledgeBaseService instance with vector store."""
    return KnowledgeBaseService(vector_store=vector_store, embedding_service=embedding)


def get_planner_service(provider: LLMProvider = Depends(get_provider)) -> PlannerService:
    """Provide PlannerService instance with injected LLM provider."""
    return PlannerService(provider=provider)


def get_coder_service(
    provider: LLMProvider = Depends(get_provider),
    knowledge_base: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> CoderService:
    """Provide CoderService instance with injected LLM provider and RAG knowledge base."""
    return CoderService(provider=provider, knowledge_base=knowledge_base)


def get_debugger_service(provider: LLMProvider = Depends(get_provider)) -> DebuggerService:
    """Provide DebuggerService instance with injected LLM provider."""
    return DebuggerService(provider=provider)


def get_sandbox_service(settings: Settings = Depends(get_app_settings)) -> SandboxService:
    """Provide SandboxService instance with injected settings."""
    return SandboxService(settings=settings)


def get_orchestrator_service(
    planner: PlannerService = Depends(get_planner_service),
    coder: CoderService = Depends(get_coder_service),
    sandbox: SandboxService = Depends(get_sandbox_service),
    debugger: DebuggerService = Depends(get_debugger_service),
) -> OrchestratorService:
    """Provide OrchestratorService instance managing the multi-agent pipeline."""
    return OrchestratorService(
        planner=planner,
        coder=coder,
        sandbox=sandbox,
        debugger=debugger,
        max_retries=2,
    )
