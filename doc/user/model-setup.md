# Model setup

The Relationship Reasoning Engine (RRE) uses **Whisper** (via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)) for local audio transcription and [Ollama](https://ollama.com/) for local LLM inference.

## Whisper (transcription)

Configure in `.env` (see `.env.example`):

| Variable | Default | Notes |
|----------|---------|-------|
| `WHISPER_MODEL` | `base` | `tiny`/`base` are faster; `small`/`medium` are slower and more accurate |
| `WHISPER_BEAM_SIZE` | `1` | Lower = faster; `5` is more accurate but slower |
| `WHISPER_VAD_FILTER` | `true` | Skips silent regions (often faster on speech with pauses) |
| `WHISPER_DEVICE` | `auto` | Set `cuda` when an NVIDIA GPU is available |
| `WHISPER_COMPUTE_TYPE` | `int8` | Use `float16` on GPU for a speed/quality balance |

The Streamlit UI calls `POST /api/transcribe/stream` and shows live progress (elapsed time, % of audio processed, segment count). The blocking `POST /api/transcribe` endpoint remains available for API clients.

Restart the API after changing Whisper settings.

## Ollama (analysis)

### Prerequisites

1. Install and start Ollama.
2. Pull at least one chat model, for example:
   ```powershell
   ollama pull llama3.2
   ```
3. Copy `.env.example` to `.env` and set a default model if you want one globally.

### Configuration layers

Model resolution follows this order (first non-empty value wins):

| Layer | Location | Example |
|-------|----------|---------|
| Request | API body `model` field | `"llama3.2"` |
| Module | `ollama_model` in `config/modules/*.yaml` | `ollama_model: llama3.2` |
| Environment | `DEFAULT_OLLAMA_MODEL` in `.env` | `DEFAULT_OLLAMA_MODEL=llama3.2` |

Legacy single-purpose analysis has been removed. Use module YAML for configuration.

## Recommended workflow

1. Set `DEFAULT_OLLAMA_MODEL` in `.env` for day-to-day use.
2. Override only modules that need a heavier or more structured model (often `meta_synthesis`).
3. Run workflows via `POST /api/workflows/{workflow_id}/run` or the Streamlit UI.
4. Stream a single module via `POST /api/modules/{module_id}/stream` when needed.

Available workflows: `quick_review`, `full_mvp`, `conflict_coaching`, `mediation_brief`, `clinical_exploration`. See [user-guide.md](user-guide.md).

## Per-module overrides

Each module YAML may set `ollama_model`. Use this when a module benefits from a different model size or style:

```yaml
id: meta_synthesis
ollama_model: llama3.1:8b
```

Leave `ollama_model: null` to inherit `DEFAULT_OLLAMA_MODEL`.

## Verify setup

```powershell
.venv\Scripts\python scripts\check_prerequisites.py
```

The Streamlit UI lists available Ollama models from `GET /api/models/ollama`.

## Long transcripts

Evidence quotes are summarized in prompts when a transcript exceeds `EVIDENCE_PROMPT_MAX_QUOTES` (default `120`). The full quote index is still stored and returned by the transcript API. Tune with:

```env
EVIDENCE_PROMPT_MAX_QUOTES=120
EVIDENCE_PROMPT_HEAD_QUOTES=80
EVIDENCE_PROMPT_TAIL_QUOTES=40
```
