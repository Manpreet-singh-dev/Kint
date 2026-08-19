"""
Claude LLM provider using the Anthropic SDK.

Wraps the Anthropic API to implement the LLMProvider protocol.
"""

from anthropic import Anthropic

from app.core.config import Settings
from app.core.exceptions import CodeGenerationError, ConfigurationError


class ClaudeProvider:
    """LLM provider implementation for Anthropic Claude models."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = self._init_client()

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

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text using Claude.

        Args:
            system_prompt: Instructions for the model's behavior.
            user_prompt: The user's input.

        Returns:
            The model's text response.
        """
        try:
            message = self._client.messages.create(
                model=self.settings.CLAUDE_MODEL,
                max_tokens=self.settings.CLAUDE_MAX_TOKENS,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )
            return message.content[0].text

        except Exception as e:
            if isinstance(e, (CodeGenerationError, ConfigurationError)):
                raise
            raise CodeGenerationError(f"Claude API call failed: {str(e)}")
