"""
LLM Provider abstraction layer.

Defines the contract that all LLM providers must implement and provides
a factory function to instantiate the correct provider based on settings.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """
    Protocol defining the interface for LLM providers.

    All LLM providers (Claude, Gemini, etc.) must implement this interface
    to be used interchangeably by the CoderService.
    """

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text from a system prompt and user prompt.

        Args:
            system_prompt: Instructions for the model's behavior and output format.
            user_prompt: The user's input/request.

        Returns:
            The model's text response.

        Raises:
            ConfigurationError: If API key is missing or invalid.
            CodeGenerationError: If the API call fails.
        """
        ...
