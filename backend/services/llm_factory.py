"""Resolve the active LLM provider from settings."""

from __future__ import annotations

from backend.services.llm_provider import LLMProvider
from config.settings import settings

_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider
    if _provider is not None:
        return _provider

    if settings.llm_provider == "bedrock":
        from backend.services.bedrock_provider import BedrockProvider

        _provider = BedrockProvider()
    else:
        from backend.services.ollama_provider import OllamaProvider

        _provider = OllamaProvider()
    return _provider


def reset_llm_provider() -> None:
    """Clear cached provider (tests)."""
    global _provider
    _provider = None
