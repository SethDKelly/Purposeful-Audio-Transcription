# Model setup

The Relationship Reasoning Engine (RRE) uses [Ollama](https://ollama.com/) for local LLM inference.

## Prerequisites

1. Install and start Ollama.
2. Pull at least one chat model, for example:
   ```powershell
   ollama pull llama3.2
   ```
3. Copy `.env.example` to `.env` and set a default model if you want one globally.

## Configuration layers

Model resolution follows this order (first non-empty value wins):

| Layer | Location | Example |
|-------|----------|---------|
| Request | API body `model` field | `"llama3.2"` |
| Module | `ollama_model` in `config/modules/*.yaml` | `ollama_model: llama3.2` |
| Environment | `DEFAULT_OLLAMA_MODEL` in `.env` | `DEFAULT_OLLAMA_MODEL=llama3.2` |

Legacy single-purpose analysis (`POST /api/analyze`, deprecated) also checks `ollama_model` in `config/purposes.yaml`.

## Per-module overrides

Each module YAML may set `ollama_model`. Use this when a module benefits from a different model size or style:

```yaml
id: meta_synthesis
ollama_model: llama3.1:8b
```

Leave `ollama_model: null` to inherit `DEFAULT_OLLAMA_MODEL`.

## Recommended workflow

1. Set `DEFAULT_OLLAMA_MODEL` in `.env` for day-to-day use.
2. Override only modules that need a heavier or more structured model (often `meta_synthesis`).
3. Run workflows via `POST /api/workflows/{workflow_id}/run` rather than the deprecated `/api/analyze` endpoint.

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
