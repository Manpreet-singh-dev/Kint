"""
Gemini LLM provider using the Google GenAI SDK.

Wraps the Google GenAI API to implement the LLMProvider protocol.
"""

from google import genai
from google.genai import types

from app.core.config import Settings
from app.core.exceptions import CodeGenerationError, ConfigurationError


class GeminiProvider:
    """LLM provider implementation for Google Gemini models."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = self._init_client()

    def _init_client(self) -> genai.Client:
        """Initialize Google GenAI client or raise ConfigurationError."""
        api_key = self.settings.GEMINI_API_KEY
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY environment variable not set. "
                "Get your key from https://aistudio.google.com/apikey",
                status_code=400,
            )
        return genai.Client(api_key=api_key)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text using Gemini.

        Args:
            system_prompt: Instructions for the model's behavior.
            user_prompt: The user's input.

        Returns:
            The model's text response.
        """
        try:
            response = self._client.models.generate_content(
                model=self.settings.GEMINI_MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=self.settings.GEMINI_MAX_TOKENS,
                    temperature=0.7,
                ),
            )
            return response.text

        except Exception as e:
            if isinstance(e, (CodeGenerationError, ConfigurationError)):
                raise
            raise CodeGenerationError(f"Gemini API call failed: {str(e)}")
