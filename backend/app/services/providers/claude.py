"""
Claude LLM provider with Anthropic Prompt Caching support (Phase 3 RAG & Caching).

Wraps the Anthropic API to implement the LLMProvider protocol with ephemeral prompt caching
on static system prompts and retrieved documentation contexts for 90% token cost reduction
and sub-second response latency.
"""

from typing import Any, Dict, List, Optional, Union
from anthropic import Anthropic

from app.core.config import Settings
from app.core.exceptions import CodeGenerationError, ConfigurationError


class ClaudeProvider:
    """LLM provider implementation for Anthropic Claude models with Prompt Caching."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = self._init_client()
        self.last_usage: Dict[str, int] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        }

    def _init_client(self) -> Anthropic:
        """Initialize Anthropic client or raise ConfigurationError."""
        api_key = self.settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get your key from https://console.anthropic.com/",
                status_code=400,
            )
        return Anthropic(api_key=api_key)

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        enable_caching: bool = True,
        cached_context: Optional[str] = None,
    ) -> str:
        """
        Generate text using Claude with prompt caching support.

        Args:
            system_prompt: Instructions for the model's behavior.
            user_prompt: The user's input or instruction.
            enable_caching: Whether to mark static blocks with ephemeral cache control.
            cached_context: Static documentation/codebase context to cache across turns.

        Returns:
            The model's text response.
        """
        try:
            # Step 1: Format system prompt with cache_control if enabled
            if enable_caching and len(system_prompt) > 100:
                system_payload: Union[str, List[Dict[str, Any]]] = [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ]
            else:
                system_payload = system_prompt

            # Step 2: Format user message content with cached RAG context block
            if enable_caching and cached_context:
                messages_payload = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": cached_context,
                                "cache_control": {"type": "ephemeral"},
                            },
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                        ],
                    }
                ]
            else:
                combined_content = f"{cached_context}\n\n{user_prompt}" if cached_context else user_prompt
                messages_payload = [
                    {
                        "role": "user",
                        "content": combined_content,
                    }
                ]

            # Step 3: Invoke Claude API
            message = self._client.messages.create(
                model=self.settings.CLAUDE_MODEL,
                max_tokens=self.settings.CLAUDE_MAX_TOKENS,
                system=system_payload,
                messages=messages_payload,
            )

            # Step 4: Record prompt cache usage metrics
            usage = getattr(message, "usage", None)
            if usage:
                self.last_usage = {
                    "input_tokens": getattr(usage, "input_tokens", 0) or 0,
                    "output_tokens": getattr(usage, "output_tokens", 0) or 0,
                    "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", 0) or 0,
                    "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0) or 0,
                }

            return message.content[0].text

        except Exception as e:
            if isinstance(e, (CodeGenerationError, ConfigurationError)):
                raise
            raise CodeGenerationError(f"Claude API call failed: {str(e)}")
