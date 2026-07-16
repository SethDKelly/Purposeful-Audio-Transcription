"""Amazon Transcribe adapter — S3 upload, async job, speaker-labeled transcript."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from backend.core.exceptions import AudioValidationError, TranscriptionError
from backend.services.transcript_types import AudioTranscriptionResult, TranscriptSegment
from config.settings import settings

logger = logging.getLogger(__name__)

_PROBE = Config(connect_timeout=2, read_timeout=5, retries={"max_attempts": 1, "mode": "standard"})
_JOB = Config(connect_timeout=10, read_timeout=60, retries={"max_attempts": 3, "mode": "standard"})

_EXT_TO_MEDIA_FORMAT = {
    ".mp3": "mp3",
    ".mp4": "mp4",
    ".m4a": "mp4",
    ".wav": "wav",
    ".flac": "flac",
    ".ogg": "ogg",
    ".amr": "amr",
    ".webm": "webm",
}


class AmazonTranscribeProvider:
    name = "transcribe"

    def __init__(self) -> None:
        region = settings.resolved_aws_region
        self._s3 = boto3.client("s3", region_name=region, config=_JOB)
        self._transcribe = boto3.client("transcribe", region_name=region, config=_JOB)

    def health_check(self) -> bool:
        if not settings.uploads_bucket.strip():
            return False
        try:
            probe = boto3.client(
                "transcribe",
                region_name=settings.resolved_aws_region,
                config=_PROBE,
            )
            probe.list_transcription_jobs(MaxResults=1)
            return True
        except (ClientError, BotoCoreError) as exc:
            logger.warning("Amazon Transcribe health check failed: %s", exc)
            return False
        except Exception as exc:  # noqa: BLE001
            logger.warning("Amazon Transcribe health check error: %s", exc)
            return False

    def transcribe(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None = None,
    ) -> AudioTranscriptionResult:
        bucket = settings.uploads_bucket.strip()
        if not bucket:
            raise AudioValidationError(
                "UPLOADS_BUCKET is not configured for Amazon Transcribe"
            )

        media_format = _media_format_for(audio_path)
        key = f"temp/transcribe/{uuid.uuid4().hex}/{audio_path.name}"
        out_key = f"temp/transcribe-out/{uuid.uuid4().hex}.json"
        job_name = f"rre-{uuid.uuid4().hex[:12]}"
        max_speakers = _max_speakers(num_speakers)

        try:
            self._s3.upload_file(str(audio_path), bucket, key)
            media_uri = f"s3://{bucket}/{key}"
            logger.info(
                "Starting Transcribe job %s media=%s max_speakers=%s",
                job_name,
                media_uri,
                max_speakers,
            )
            start_kwargs: dict = {
                "TranscriptionJobName": job_name,
                "Media": {"MediaFileUri": media_uri},
                "MediaFormat": media_format,
                "OutputBucketName": bucket,
                "OutputKey": out_key,
                "Settings": {
                    "ShowSpeakerLabels": True,
                    "MaxSpeakerLabels": max_speakers,
                },
            }
            language = settings.transcribe_language.strip() or "en-US"
            start_kwargs["LanguageCode"] = language

            self._transcribe.start_transcription_job(**start_kwargs)
            self._wait_for_job(job_name)
            payload = self._load_transcript_json(bucket, out_key)
            return _result_from_transcribe_json(
                payload, speaker_prefix=settings.speaker_prefix
            )
        except (ClientError, BotoCoreError) as exc:
            logger.exception("Amazon Transcribe failed for %s", audio_path.name)
            raise TranscriptionError(f"Amazon Transcribe failed: {exc}") from exc
        finally:
            for cleanup_key in (key, out_key):
                try:
                    self._s3.delete_object(Bucket=bucket, Key=cleanup_key)
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "Failed to delete temp object s3://%s/%s: %s",
                        bucket,
                        cleanup_key,
                        exc,
                    )

    def _wait_for_job(self, job_name: str) -> None:
        deadline = time.monotonic() + max(30.0, settings.transcribe_timeout_seconds)
        poll = max(1.0, settings.transcribe_poll_seconds)
        while time.monotonic() < deadline:
            response = self._transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job = response["TranscriptionJob"]
            status = job["TranscriptionJobStatus"]
            if status == "COMPLETED":
                return
            if status == "FAILED":
                reason = job.get("FailureReason") or "unknown"
                raise TranscriptionError(f"Amazon Transcribe job failed: {reason}")
            time.sleep(poll)
        raise TranscriptionError(
            f"Amazon Transcribe job timed out after {settings.transcribe_timeout_seconds}s"
        )

    def _load_transcript_json(self, bucket: str, key: str) -> dict:
        # Read via S3 API so Stage B (no public egress) works through the gateway endpoint.
        obj = self._s3.get_object(Bucket=bucket, Key=key)
        return json.loads(obj["Body"].read().decode("utf-8"))


def _media_format_for(audio_path: Path) -> str:
    ext = audio_path.suffix.lower()
    fmt = _EXT_TO_MEDIA_FORMAT.get(ext)
    if not fmt:
        raise AudioValidationError(
            f"Unsupported audio extension for Transcribe: {ext or '(none)'}. "
            f"Supported: {', '.join(sorted(_EXT_TO_MEDIA_FORMAT))}"
        )
    return fmt


def _max_speakers(num_speakers: int | None) -> int:
    if num_speakers is not None:
        return max(2, min(10, num_speakers))
    configured = settings.transcribe_max_speakers
    return max(2, min(10, configured))


def _result_from_transcribe_json(
    payload: dict,
    *,
    speaker_prefix: str = "Person",
) -> AudioTranscriptionResult:
    """Map Transcribe JSON to labeled Person A/B text expected by TranscriptParser."""
    results = payload.get("results") or {}
    items = results.get("items") or []
    transcripts = results.get("transcripts") or []
    plain = (transcripts[0].get("transcript") if transcripts else "") or ""

    speaker_map: dict[str, str] = {}
    turns: list[tuple[str, str]] = []
    current_speaker: str | None = None
    current_parts: list[str] = []
    segments: list[TranscriptSegment] = []

    def flush() -> None:
        nonlocal current_speaker, current_parts
        if current_speaker and current_parts:
            text = "".join(current_parts).strip()
            if text:
                turns.append((current_speaker, text))
        current_parts = []

    for item in items:
        item_type = item.get("type")
        alts = item.get("alternatives") or []
        content = (alts[0].get("content") if alts else "") or ""
        if item_type == "punctuation":
            if current_parts:
                current_parts.append(content)
            continue

        raw_label = item.get("speaker_label") or "spk_0"
        label = speaker_map.setdefault(
            raw_label,
            _display_label(len(speaker_map), speaker_prefix),
        )
        if label != current_speaker:
            flush()
            current_speaker = label

        if current_parts and not current_parts[-1].endswith((" ", "\n")):
            # Transcribe pronunciation items are space-separated words.
            current_parts.append(" ")
        current_parts.append(content)

        start = item.get("start_time")
        end = item.get("end_time")
        if start is not None and end is not None and content:
            try:
                segments.append(
                    TranscriptSegment(
                        start=float(start),
                        end=float(end),
                        text=content,
                    )
                )
            except (TypeError, ValueError):
                pass

    flush()

    if turns:
        labeled_text = "\n".join(f"{speaker}: {text}" for speaker, text in turns)
        labels = list(dict.fromkeys(speaker for speaker, _ in turns))
    else:
        labeled_text = plain.strip() or ""
        labels = ["Person A"] if labeled_text else []
        if labeled_text and not labeled_text.startswith("Person "):
            labeled_text = f"Person A: {labeled_text}"

    if not labeled_text.strip():
        raise TranscriptionError("Amazon Transcribe returned an empty transcript")

    duration = segments[-1].end if segments else None
    return AudioTranscriptionResult(
        text=labeled_text,
        segments=segments,
        language=_language_from_payload(payload),
        duration_seconds=duration,
        speaker_count=max(1, len(labels)),
        speaker_labels=labels,
        diarization_applied=bool(speaker_map) or len(labels) > 1,
        diarization_skip_reason=None if (speaker_map or len(labels) > 1) else "no_speaker_labels",
        transcription_mode="transcribe",
    )


def _display_label(index: int, prefix: str) -> str:
    # Person A, Person B, ... then Person 27 etc. after Z
    if index < 26:
        return f"{prefix} {chr(ord('A') + index)}"
    return f"{prefix} {index + 1}"


def _language_from_payload(payload: dict) -> str | None:
    results = payload.get("results") or {}
    lang = results.get("language_code")
    if lang:
        return str(lang)
    job = payload.get("TranscriptionJob") or {}
    return job.get("LanguageCode")
