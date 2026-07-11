"""LLM provider protocol — Ollama (local) and Bedrock (AWS)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol


class LLMProvider(Protocol):
    @property
    def name(self) -> str: ...

    def health_check(self) -> bool: ...

    def list_models(self) -> list[str]: ...

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        json_mode: bool = False,
    ) -> str: ...

    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> Iterator[str]: ...
