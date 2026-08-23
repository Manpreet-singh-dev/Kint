"""Tests for ClaudeProvider with Anthropic Prompt Caching (Phase 3)."""

import pytest
from unittest.mock import MagicMock, patch

from app.core.config import Settings
from app.services.providers.claude import ClaudeProvider


def test_claude_prompt_caching_payload_structure():
    """Test ClaudeProvider creates ephemeral cache_control blocks for system and context."""
    settings = Settings(
        ANTHROPIC_API_KEY="test_anthropic_key",
        LLM_PROVIDER="claude",
    )

    with patch("app.services.providers.claude.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Generated code response")]
        mock_message.usage = MagicMock(
            input_tokens=150,
            output_tokens=300,
            cache_creation_input_tokens=1200,
            cache_read_input_tokens=0,
        )
        mock_client.messages.create.return_value = mock_message

        provider = ClaudeProvider(settings=settings)
        system_text = "You are an expert coder. " * 10
        cached_doc = "--- FastAPI Patterns ---\nUse Depends for DI."
        user_text = "Create a login router."

        response = provider.generate_text(
            system_prompt=system_text,
            user_prompt=user_text,
            enable_caching=True,
            cached_context=cached_doc,
        )

        assert response == "Generated code response"
        mock_client.messages.create.assert_called_once()

        call_kwargs = mock_client.messages.create.call_args.kwargs
        # Verify system prompt has cache_control
        assert isinstance(call_kwargs["system"], list)
        assert call_kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}

        # Verify messages content has cached_context with cache_control
        messages = call_kwargs["messages"]
        assert len(messages) == 1
        content_blocks = messages[0]["content"]
        assert isinstance(content_blocks, list)
        assert content_blocks[0]["text"] == cached_doc
        assert content_blocks[0]["cache_control"] == {"type": "ephemeral"}
        assert content_blocks[1]["text"] == user_text

        # Verify usage metrics recorded
        assert provider.last_usage["cache_creation_input_tokens"] == 1200
        assert provider.last_usage["output_tokens"] == 300


def test_claude_caching_disabled():
    """Test ClaudeProvider formats regular strings when caching is disabled."""
    settings = Settings(
        ANTHROPIC_API_KEY="test_anthropic_key",
        LLM_PROVIDER="claude",
    )

    with patch("app.services.providers.claude.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Plain response")]
        mock_message.usage = MagicMock(input_tokens=50, output_tokens=20)
        mock_client.messages.create.return_value = mock_message

        provider = ClaudeProvider(settings=settings)
        provider.generate_text(
            system_prompt="Short prompt",
            user_prompt="Hi",
            enable_caching=False,
        )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["system"] == "Short prompt"
        assert call_kwargs["messages"] == [{"role": "user", "content": "Hi"}]
