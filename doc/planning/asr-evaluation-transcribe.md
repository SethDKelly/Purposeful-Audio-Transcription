# ASR evaluation note — Whisper vs Amazon Transcribe (AWS-1c)

Formal record of the ASR approach for RRE after P1-1 implementation.

| | |
|---|---|
| **Status** | **Accepted** — AWS Stage B live burn-in 2026-07-14 |
| **Date** | 2026-07-14 |
| **Local** | Whisper (`faster-whisper`) + optional pyannote (`TRANSCRIPTION_PROVIDER=whisper`, `.[local]`) |
| **AWS** | Amazon Transcribe async jobs + speaker labels (`TRANSCRIPTION_PROVIDER=transcribe`, `Dockerfile.cloud`) |

---

## Decision

| Environment | ASR | Speakers |
|-------------|-----|----------|
| **Local** | Whisper | pyannote (or single-speaker) |
| **AWS** | Amazon Transcribe | Transcribe `ShowSpeakerLabels` → `Person A` / `Person B` labeled lines |

Cloud image does **not** depend on Hugging Face or torch/pyannote (`Dockerfile.cloud` / P1-2).

---

## Why Transcribe on AWS

1. **No-egress compatible** — VPC `transcribe` endpoint + S3 gateway; transcript JSON written to `UPLOADS_BUCKET` (not public `TranscriptFileUri` fetch).
2. **Removes HF_TOKEN / pyannote** from ECS — closes the interim diarization egress hole (AWS-5g skipped).
3. **Slimmer image** — drop torch, faster-whisper, pyannote.
4. **Managed scaling** — no Fargate CPU spikes for Whisper on long audio.

Whisper remains the local path (`TRANSCRIPTION_PROVIDER=whisper`).

---

## Implementation (code)

| Piece | Location |
|-------|----------|
| Protocol | `backend/services/transcription_provider.py` |
| Factory | `backend/services/transcription_factory.py` |
| Whisper | `whisper_transcription_provider.py` → `AudioTranscriptionService` |
| Transcribe | `amazon_transcribe_provider.py` — S3 upload, job, S3 output JSON, labeled turns |
| Routes | `/api/transcribe` + orchestrator via `get_transcription_provider()` |

Settings: `TRANSCRIPTION_PROVIDER`, `UPLOADS_BUCKET`, `TRANSCRIBE_LANGUAGE` (default `en-US`), poll/timeout.

---

## Evaluation checklist

### Functional

- [x] Async job: upload audio to S3 → `StartTranscriptionJob` → poll → read JSON from output bucket
- [x] Speaker labels map to `Person A` / `Person B` turns
- [x] Output maps into existing ingest (`TranscriptParser` labeled text)
- [x] Failure modes: missing bucket, unsupported format, job failed — raised as app errors
- [x] Unit tests for mapping + mocked job path
- [x] **Live AWS:** short audio upload under Stage B + Transcribe job + Quick Review on Bedrock (2026-07-14)

### Quality (compare vs sliced Whisper+pyannote)

- [ ] 3–5 golden audio fixtures (short dialogue, overlap, quiet speaker)
- [ ] Speaker confusion rate and turn boundary quality (human spot-check)
- [ ] Timestamp presence/absence vs evidence quote flow

### Ops / security

- [x] Task role includes Transcribe + S3 (iam.tf)
- [x] Temp audio + transcript JSON deleted in `finally` (app); S3 lifecycle **1 day** on `temp/` (P1-3a)
- [ ] No transcript body in CloudWatch (P1-3c)
- [x] VPC endpoint smoke: Transcribe job with Stage B tasks (slim deploy burn-in)

### Live burn-in notes (2026-07-14)

| Step | Result |
|------|--------|
| Synthesized short WAV → `POST /api/transcribe` | HTTP 200, `transcription_mode=transcribe` |
| Speaker labels | Single speaker (TTS); job + S3 output path OK |
| Ingest + Quick Review | Run `001f5d84-…` **completed**; 3/3 modules on Bedrock |
| Staging | Artifacts in `data/temp/burnin-*` (local) |

---

## Explicit non-goals

- Replacing ffmpeg for local diarization decode
- Torchcodec as primary decode ([aws-deployment.md](aws-deployment.md) §5)
- Multi-language IdentifyLanguage with speaker labels (LanguageCode required; default `en-US`)
