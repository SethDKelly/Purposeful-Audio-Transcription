"""Ollama-backed LLM provider for local development."""

from __future__ import annotations

from collections.abc import Iterator

from backend.services.ollama_service import OllamaService, ollama_service


class OllamaProvider:
    name = "ollama"

    def __init__(self, service: OllamaService | None = None) -> None:
        self._service = service or ollama_service

    def health_check(self) -> bool:
        return self._service.health_check()

    def list_models(self) -> list[str]:
        return self._service.list_models()

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        json_mode: bool = False,
    ) -> str:
        return self._service.chat(model, messages, json_mode=json_mode)

    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        yield from self._service.chat_stream(model, messages)
