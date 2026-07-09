import logging
from pathlib import Path

from backend.core.exceptions import AnalysisError
from backend.services.analysis_service import analysis_service
from backend.services.whisper_service import TranscriptResult, whisper_service

logger = logging.getLogger(__name__)


class Orchestrator:
    def transcribe(self, audio_path: Path) -> TranscriptResult:
        return whisper_service.transcribe(audio_path)

    def process(
        self,
        audio_path: Path,
        purpose_id: str,
        model: str | None = None,
    ) -> dict:
        logger.info("Processing audio with purpose=%s", purpose_id)
        transcript_result = self.transcribe(audio_path)
        if not transcript_result.text.strip():
            raise AnalysisError("Transcription produced empty text")

        analysis_result = analysis_service.analyze(
            transcript=transcript_result.text,
            purpose_id=purpose_id,
            model=model,
        )

        return {
            "transcript": transcript_result.text,
            "segments": [
                {"start": seg.start, "end": seg.end, "text": seg.text}
                for seg in transcript_result.segments
            ],
            "language": transcript_result.language,
            "duration_seconds": transcript_result.duration_seconds,
            **analysis_result,
        }


orchestrator = Orchestrator()
