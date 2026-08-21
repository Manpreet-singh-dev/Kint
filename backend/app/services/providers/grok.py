"""
Grok (xAI) and Groq (Groq Cloud) LLM provider.

Wraps the OpenAI-compatible REST API for xAI (Grok) and Groq Cloud.
Automatically detects Groq keys (gsk_...) and routes to the correct endpoint.
"""

import httpx

from app.core.config import Settings
from app.core.exceptions import CodeGenerationError, ConfigurationError


class GrokProvider:
    """LLM provider implementation for xAI Grok and Groq Cloud models."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = self._get_api_key()
        self.is_groq = self._detect_groq()
        self.base_url, self.model, self.max_tokens = self._configure_endpoint()

    def _get_api_key(self) -> str:
        """Retrieve Grok/Groq/xAI API key or raise ConfigurationError."""
        api_key = (
            self.settings.GROK_API_KEY
            or self.settings.GROQ_API_KEY
            or self.settings.XAI_API_KEY
        )
        if not api_key:
            raise ConfigurationError(
                "GROK_API_KEY / GROQ_API_KEY environment variable not set. "
                "For Groq: get key from https://console.groq.com/keys | "
                "For xAI Grok: get key from https://console.x.ai/",
                status_code=400,
            )
        return api_key.strip()

    def _detect_groq(self) -> bool:
        """Check if provider or key is Groq Cloud (gsk_ prefix or groq provider name)."""
        provider_name = self.settings.LLM_PROVIDER.lower()
        if provider_name == "groq" or self.settings.GROQ_API_KEY:
            return True
        if self.api_key.startswith("gsk_"):
            return True
        return False

    def _configure_endpoint(self) -> tuple[str, str, int]:
        """Resolve base URL, model name, and max tokens for xAI vs Groq."""
        if self.is_groq:
            base_url = self.settings.GROQ_BASE_URL
            model = self.settings.GROQ_MODEL
            # If user configured a custom GROK_MODEL that looks like a Groq model or general model, use it
            if self.settings.GROK_MODEL and self.settings.GROK_MODEL != "grok-2-1212" and not self.settings.GROK_MODEL.startswith("grok-"):
                model = self.settings.GROK_MODEL
            max_tokens = self.settings.GROQ_MAX_TOKENS
        else:
            base_url = self.settings.GROK_BASE_URL
            model = self.settings.GROK_MODEL
            max_tokens = self.settings.GROK_MAX_TOKENS

        return base_url, model, max_tokens

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text using Grok / Groq.

        Args:
            system_prompt: Instructions for the model's behavior.
            user_prompt: The user's input.

        Returns:
            The model's text response.
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.7,
        }

        provider_label = "Groq" if self.is_groq else "Grok"
        max_attempts = 4

        for attempt in range(max_attempts):
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(url, json=payload, headers=headers)

                if response.status_code == 429 and attempt < max_attempts - 1:
                    # Rate limit hit: parse retry-after or wait 10 seconds
                    wait_seconds = 10.0
                    try:
                        error_json = response.json()
                        error_msg = error_json.get("error", {}).get("message", "")
                        match = re.search(r"try again in ([\d\.]+)s", error_msg)
                        if match:
                            wait_seconds = float(match.group(1)) + 1.0
                    except Exception:
                        pass
                    import time
                    time.sleep(wait_seconds)
                    continue

                if response.status_code != 200:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", response.text)
                    except Exception:
                        pass
                    raise CodeGenerationError(
                        f"{provider_label} API call failed (HTTP {response.status_code}): {error_detail}"
                    )

                data = response.json()
                choices = data.get("choices", [])
                if not choices or "message" not in choices[0]:
                    raise CodeGenerationError(f"{provider_label} API returned an empty or invalid response.")

                return choices[0]["message"].get("content", "")

            except Exception as e:
                if isinstance(e, (CodeGenerationError, ConfigurationError)):
                    raise
                if attempt < max_attempts - 1 and "429" in str(e):
                    import time
                    time.sleep(10.0)
                    continue
                raise CodeGenerationError(f"{provider_label} API call failed: {str(e)}")
