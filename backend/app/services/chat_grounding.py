"""
Chat Grounding Service (Phase 3 RAG & Code Q&A).

Role in Pipeline:
Provides conversational Q&A grounded in an indexed application's codebase.
Retrieves relevant code snippets from PostgreSQL + pgvector via AppIndexerService
and injects them as grounding context into the LLM prompt.
"""

from typing import List, Optional

from app.schemas.chat import ChatMessage, ChatResponse, CodeSourceCitation
from app.services.app_indexer import AppIndexerService
from app.services.providers.base import LLMProvider


CHAT_GROUNDING_SYSTEM_PROMPT = """You are an expert software developer and technical assistant for this specific web application.
Your goal is to answer questions, explain architectural decisions, describe how components work, and recommend modifications based strictly on the provided codebase excerpts.

Guidelines:
1. Ground your answers in the provided code snippets.
2. Reference specific filenames (e.g. index.html, style.css, script.js), function names, and CSS classes when explaining.
3. If the user asks how to modify or extend the application, provide concrete code examples that integrate cleanly with the existing code.
4. If a question cannot be answered from the provided code context, state clearly what is known and what is missing.
"""

CHAT_GROUNDING_PROMPT_TEMPLATE = """Application ID: {app_id}

Retrieved Codebase Context:
{code_context}

{history_section}User Question:
{message}

Please provide a clear, accurate, grounded response."""


class ChatGroundingService:
    """Service handling codebase-grounded conversational Q&A."""

    def __init__(
        self,
        provider: LLMProvider,
        app_indexer: AppIndexerService,
    ):
        self.provider = provider
        self.app_indexer = app_indexer

    def answer_question(
        self,
        app_id: str,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> ChatResponse:
        """
        Answer a question grounded in the target application's vector-indexed codebase.

        Args:
            app_id: Identifier of the indexed application.
            message: User's question or instruction.
            history: Optional list of previous chat messages.

        Returns:
            ChatResponse containing the AI answer and cited code sources.
        """
        # Step 1: Retrieve top-k relevant code chunks for the question
        code_chunks = self.app_indexer.query_app_code(
            app_id=app_id,
            query=message,
            limit=4,
        )

        # Step 2: Format citations and prompt context
        sources: List[CodeSourceCitation] = []
        context_blocks = []

        for chunk in code_chunks:
            file_name = chunk.metadata.get("file_name", "unknown")
            section_name = chunk.metadata.get("section_name")
            sources.append(
                CodeSourceCitation(
                    file_name=file_name,
                    section_name=section_name,
                    content=chunk.content[:300],  # Concise excerpt for citation
                    similarity_score=round(chunk.similarity_score, 4),
                )
            )
            context_blocks.append(
                f"--- File: {file_name} ({section_name or 'code block'}) ---\n{chunk.content}"
            )

        code_context = "\n\n".join(context_blocks) if context_blocks else "(No indexed code chunks found for this query/app)"

        # Step 3: Format conversation history
        history_section = ""
        if history:
            formatted_turns = []
            for turn in history[-6:]:  # Keep last 6 turns
                role_label = "User" if turn.role == "user" else "Assistant"
                formatted_turns.append(f"{role_label}: {turn.content}")
            history_section = "Conversation History:\n" + "\n".join(formatted_turns) + "\n\n"

        user_prompt = CHAT_GROUNDING_PROMPT_TEMPLATE.format(
            app_id=app_id,
            code_context=code_context,
            history_section=history_section,
            message=message,
        )

        # Step 4: Generate response via LLM provider
        response_text = self.provider.generate_text(
            system_prompt=CHAT_GROUNDING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ChatResponse(
            app_id=app_id,
            response=response_text,
            sources=sources,
        )
