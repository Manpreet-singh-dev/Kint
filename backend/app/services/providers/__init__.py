"""
LLM Provider package.

Provides a factory function to create the correct LLM provider based on
application settings. Supports switching between Claude and Gemini via
the LLM_PROVIDER environment variable.
"""

from app.core.config import Settings
from app.core.exceptions import ConfigurationError
from app.services.providers.base import LLMProvider


def get_llm_provider(settings: Settings) -> LLMProvider:
    """
    Factory function to create the appropriate LLM provider.

    Args:
        settings: Application settings containing LLM_PROVIDER and API keys.

    Returns:
        An LLMProvider instance (ClaudeProvider or GeminiProvider).

    Raises:
        ConfigurationError: If the specified provider is not supported.
    """
    provider_name = settings.LLM_PROVIDER.lower()

    if provider_name == "claude":
        from app.services.providers.claude import ClaudeProvider
        return ClaudeProvider(settings=settings)

    elif provider_name == "gemini":
        from app.services.providers.gemini import GeminiProvider
        return GeminiProvider(settings=settings)

    elif provider_name in ("grok", "xai", "groq"):
        from app.services.providers.grok import GrokProvider
        return GrokProvider(settings=settings)

    else:
        raise ConfigurationError(
            f"Unsupported LLM provider: '{settings.LLM_PROVIDER}'. "
            f"Supported providers: 'claude', 'gemini', 'grok', 'groq'.",
            status_code=400,
        )


__all__ = ["LLMProvider", "get_llm_provider"]
