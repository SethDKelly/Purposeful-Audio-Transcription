"""Resolve the active LLM provider (Bedrock only)."""

from __future__ import annotations

from backend.services.bedrock_provider import BedrockProvider
from backend.services.llm_provider import LLMProvider

_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider
    if _provider is not None:
        return _provider
    _provider = BedrockProvider()
    return _provider


def reset_llm_provider() -> None:
    """Clear cached provider (tests)."""
    global _provider
    _provider = None
