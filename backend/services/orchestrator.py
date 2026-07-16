import logging
from pathlib import Path

from backend.core.exceptions import AnalysisError
from backend.core.workflow_registry import workflow_registry
from backend.services.transcript_types import AudioTranscriptionResult
from backend.services.transcription_factory import get_transcription_provider
from backend.services.transcript_service import transcript_service
from backend.services.workflow_engine import build_workflow_analysis_text, workflow_engine

logger = logging.getLogger(__name__)


class Orchestrator:
    def transcribe(self, audio_path: Path) -> AudioTranscriptionResult:
        return get_transcription_provider().transcribe(audio_path)

    def process_workflow(
        self,
        audio_path: Path,
        workflow_id: str,
        model: str | None = None,
    ) -> dict:
        logger.info("Processing audio with workflow=%s", workflow_id)
        workflow = workflow_registry.get(workflow_id)
        transcript_result = self.transcribe(audio_path)
        if not transcript_result.text.strip():
            raise AnalysisError("Transcription produced empty text")

        bundle = transcript_service.ingest_from_audio(
            raw_text=transcript_result.text,
            language=transcript_result.language,
        )
        workflow_run = workflow_engine.run(
            workflow_id=workflow_id,
            transcript_id=bundle.transcript.id,
            model=model,
        )
        _, module_runs = workflow_engine.get_with_module_runs(workflow_run.id)
        analysis = build_workflow_analysis_text(workflow, module_runs)

        resolved_model = model or workflow_run.model_used or ""
        return {
            "transcript": transcript_result.text,
            "segments": [
                {"start": seg.start, "end": seg.end, "text": seg.text}
                for seg in transcript_result.segments
            ],
            "language": transcript_result.language,
            "duration_seconds": transcript_result.duration_seconds,
            "speaker_count": transcript_result.speaker_count,
            "speaker_labels": transcript_result.speaker_labels,
            "diarization_applied": transcript_result.diarization_applied,
            "model": resolved_model,
            "analysis": analysis,
            "workflow_id": workflow.config.id,
            "workflow_name": workflow.config.name,
            "workflow_run_id": workflow_run.id,
            "transcript_id": bundle.transcript.id,
        }


orchestrator = Orchestrator()
