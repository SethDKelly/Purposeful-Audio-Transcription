import logging
from collections.abc import Iterator
from typing import Any

import httpx
import ollama

from config.settings import settings
from backend.core.exceptions import OllamaError

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self) -> None:
        self._client = ollama.Client(host=settings.ollama_host)

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{settings.ollama_host}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return False

    def list_models(self) -> list[str]:
        try:
            response = self._client.list()
            return sorted(model.model for model in response.models)
        except Exception as exc:
            raise OllamaError(f"Failed to list Ollama models: {exc}") from exc

    def _chat_options(self, *, think: bool | None = None) -> dict[str, Any]:
        resolved = settings.ollama_think if think is None else think
        return {"think": resolved}

    @staticmethod
    def _message_thinking(message: Any) -> str:
        return getattr(message, "thinking", None) or ""

    def _empty_response_error(self, response: Any, *, think: bool) -> OllamaError:
        thinking = self._message_thinking(response.message)
        if thinking:
            return OllamaError(
                "Ollama returned an empty response: model output went to the thinking "
                f"field ({len(thinking)} chars). Set OLLAMA_THINK=false or use a model "
                "without built-in thinking for structured JSON workflows."
            )
        return OllamaError("Ollama returned an empty response")

    def chat(self, model: str, messages: list[dict[str, str]]) -> str:
        try:
            think = settings.ollama_think
            response = self._client.chat(
                model=model,
                messages=messages,
                **self._chat_options(think=think),
            )
            content = response.message.content
            if content:
                return content

            if think and self._message_thinking(response.message):
                logger.warning(
                    "Ollama returned empty content with thinking enabled; retrying with think=false"
                )
                response = self._client.chat(
                    model=model,
                    messages=messages,
                    **self._chat_options(think=False),
                )
                content = response.message.content
                if content:
                    return content

            raise self._empty_response_error(response, think=think)
        except OllamaError:
            raise
        except Exception as exc:
            raise OllamaError(f"Ollama chat failed: {exc}") from exc

    def chat_stream(
        self, model: str, messages: list[dict[str, str]]
    ) -> Iterator[str]:
        try:
            stream = self._client.chat(
                model=model,
                messages=messages,
                stream=True,
                **self._chat_options(),
            )
            for chunk in stream:
                if chunk.message and chunk.message.content:
                    yield chunk.message.content
        except Exception as exc:
            raise OllamaError(f"Ollama streaming chat failed: {exc}") from exc


ollama_service = OllamaService()
