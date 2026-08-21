"""Tests for Grok (xAI) LLM Provider."""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.core.config import Settings
from app.core.exceptions import CodeGenerationError, ConfigurationError
from app.services.providers import get_llm_provider
from app.services.providers.grok import GrokProvider
from app.services.coder import CoderService


def test_grok_provider_missing_api_key():
    """Test GrokProvider raises ConfigurationError if API key is missing."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY=None,
        XAI_API_KEY=None,
    )
    with pytest.raises(ConfigurationError) as excinfo:
        GrokProvider(settings=settings)
    assert "GROK_API_KEY" in excinfo.value.message


def test_grok_provider_init_with_grok_api_key():
    """Test GrokProvider successfully initializes with GROK_API_KEY."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="xai-test-key-123",
    )
    provider = GrokProvider(settings=settings)
    assert provider.api_key == "xai-test-key-123"


def test_grok_provider_init_with_xai_api_key():
    """Test GrokProvider successfully initializes with XAI_API_KEY fallback."""
    settings = Settings(
        LLM_PROVIDER="xai",
        GROK_API_KEY=None,
        XAI_API_KEY="xai-alt-key-456",
    )
    provider = GrokProvider(settings=settings)
    assert provider.api_key == "xai-alt-key-456"


def test_grok_provider_generate_text_success():
    """Test GrokProvider.generate_text sends correct request and returns model response."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="xai-test-key",
        GROK_MODEL="grok-2-latest",
    )
    provider = GrokProvider(settings=settings)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "```index.html\n<!DOCTYPE html><html><body><h1>Hello Grok</h1></body></html>\n```",
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_response) as mock_post:
        result = provider.generate_text("System prompt", "User prompt")
        assert "Hello Grok" in result
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer xai-test-key"
        assert kwargs["json"]["model"] == "grok-2-latest"
        assert kwargs["json"]["messages"][0]["content"] == "System prompt"
        assert kwargs["json"]["messages"][1]["content"] == "User prompt"


def test_grok_provider_generate_text_api_error():
    """Test GrokProvider raises CodeGenerationError when xAI API returns an error status."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="xai-test-key",
    )
    provider = GrokProvider(settings=settings)

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = '{"error": {"message": "Incorrect API key provided"}}'
    mock_response.json.return_value = {"error": {"message": "Incorrect API key provided"}}

    with patch("httpx.Client.post", return_value=mock_response):
        with pytest.raises(CodeGenerationError) as excinfo:
            provider.generate_text("System prompt", "User prompt")
        assert "Incorrect API key provided" in excinfo.value.message


def test_grok_provider_generate_text_network_failure():
    """Test GrokProvider handles connection exceptions."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="xai-test-key",
    )
    provider = GrokProvider(settings=settings)

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Connection timed out")):
        with pytest.raises(CodeGenerationError) as excinfo:
            provider.generate_text("System prompt", "User prompt")
        assert "Connection timed out" in excinfo.value.message


def test_get_llm_provider_factory_grok():
    """Test get_llm_provider instantiates GrokProvider for 'grok' and 'xai'."""
    settings_grok = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="xai-key",
    )
    provider = get_llm_provider(settings_grok)
    assert isinstance(provider, GrokProvider)

    settings_xai = Settings(
        LLM_PROVIDER="xai",
        XAI_API_KEY="xai-key",
    )
    provider_xai = get_llm_provider(settings_xai)
    assert isinstance(provider_xai, GrokProvider)


def test_groq_key_autodetection_and_routing():
    """Test that gsk_ keys automatically route to Groq Cloud endpoint with gpt-oss model."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="gsk_1234567890abcdef",
    )
    provider = GrokProvider(settings=settings)
    assert provider.is_groq is True
    assert provider.base_url == "https://api.groq.com/openai/v1"
    assert provider.model == "openai/gpt-oss-120b"


def test_groq_provider_explicit():
    """Test LLM_PROVIDER='groq' routes to Groq Cloud endpoint."""
    settings = Settings(
        LLM_PROVIDER="groq",
        GROK_API_KEY=None,
        GROQ_API_KEY="gsk_explicit_key",
    )
    provider = get_llm_provider(settings)
    assert isinstance(provider, GrokProvider)
    assert provider.is_groq is True
    assert provider.model == "openai/gpt-oss-120b"


def test_coder_service_integration_with_grok_provider():
    """Test CoderService parses files generated via GrokProvider."""
    settings = Settings(
        LLM_PROVIDER="grok",
        GROK_API_KEY="xai-test-key",
    )
    provider = GrokProvider(settings=settings)
    coder = CoderService(provider=provider)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "```index.html\n<!DOCTYPE html><html><body><h1>Grok App</h1></body></html>\n```\n```style.css\nbody { background: #000; }\n```",
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_response):
        files = coder.generate_files("Build a Grok test app")
        assert "index.html" in files
        assert "style.css" in files
        assert "Grok App" in files["index.html"]
