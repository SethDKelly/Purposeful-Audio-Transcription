import logging
from collections.abc import Iterator

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

    def chat(self, model: str, messages: list[dict[str, str]]) -> str:
        try:
            response = self._client.chat(model=model, messages=messages)
            content = response.message.content
            if not content:
                raise OllamaError("Ollama returned an empty response")
            return content
        except OllamaError:
            raise
        except Exception as exc:
            raise OllamaError(f"Ollama chat failed: {exc}") from exc

    def chat_stream(
        self, model: str, messages: list[dict[str, str]]
    ) -> Iterator[str]:
        try:
            stream = self._client.chat(model=model, messages=messages, stream=True)
            for chunk in stream:
                if chunk.message and chunk.message.content:
                    yield chunk.message.content
        except Exception as exc:
            raise OllamaError(f"Ollama streaming chat failed: {exc}") from exc


ollama_service = OllamaService()
