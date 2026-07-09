import logging
from collections.abc import Iterator

from config.settings import settings
from backend.core.exceptions import AnalysisError, OllamaError, PurposeNotFoundError
from backend.core.purpose_registry import purpose_registry
from backend.services.ollama_service import ollama_service

logger = logging.getLogger(__name__)


class AnalysisService:
    def _resolve_model(self, purpose_id: str, model: str | None) -> tuple[str, object]:
        try:
            purpose = purpose_registry.get(purpose_id)
        except PurposeNotFoundError as exc:
            raise AnalysisError(str(exc.message)) from exc

        resolved_model = (
            model or purpose.ollama_model or settings.default_ollama_model or None
        )
        if not resolved_model:
            raise AnalysisError(
                "No Ollama model specified. Select a model in the UI, set "
                "ollama_model in purposes.yaml, or set DEFAULT_OLLAMA_MODEL in .env."
            )
        return resolved_model, purpose

    def analyze(
        self,
        transcript: str,
        purpose_id: str,
        model: str | None = None,
    ) -> dict[str, str]:
        transcript = transcript.strip()
        if not transcript:
            raise AnalysisError("Transcript is empty")

        resolved_model, purpose = self._resolve_model(purpose_id, model)
        messages = purpose_registry.build_messages(purpose_id, transcript)
        logger.info(
            "Analyzing transcript with purpose=%s model=%s",
            purpose_id,
            resolved_model,
        )

        try:
            analysis = ollama_service.chat(resolved_model, messages)
        except OllamaError as exc:
            raise AnalysisError(str(exc.message)) from exc

        return {
            "purpose_id": purpose.id,
            "purpose_name": purpose.name,
            "model": resolved_model,
            "analysis": analysis,
        }

    def analyze_stream(
        self,
        transcript: str,
        purpose_id: str,
        model: str | None = None,
    ) -> Iterator[str]:
        transcript = transcript.strip()
        if not transcript:
            raise AnalysisError("Transcript is empty")

        resolved_model, _purpose = self._resolve_model(purpose_id, model)
        messages = purpose_registry.build_messages(purpose_id, transcript)
        logger.info(
            "Streaming analysis with purpose=%s model=%s",
            purpose_id,
            resolved_model,
        )

        try:
            yield from ollama_service.chat_stream(resolved_model, messages)
        except OllamaError as exc:
            raise AnalysisError(str(exc.message)) from exc


analysis_service = AnalysisService()
