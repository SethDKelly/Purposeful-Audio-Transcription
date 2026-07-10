# Model setup

The Relationship Reasoning Engine (RRE) uses **Whisper** (via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)) for local audio transcription and [Ollama](https://ollama.com/) for local LLM inference.

## Whisper (transcription)

Configure in `.env` (see `.env.example`):

| Variable | Default | Notes |
|----------|---------|-------|
| `WHISPER_MODEL` | `base` | `tiny`/`base` faster; `small`/`medium` more accurate |
| `WHISPER_DEVICE` | `auto` | `auto` picks CUDA if available, else CPU |
| `WHISPER_COMPUTE_TYPE` | `int8` | On CUDA, `int8` is automatically promoted to `float16` |

## GPU / accelerator setup

Whisper and pyannote diarization share the same device preference order: **CUDA → MPS (Mac) → CPU**.

| Variable | Default | Notes |
|----------|---------|-------|
| `WHISPER_DEVICE` | `auto` | `auto` / `cuda` / `cpu` (MPS falls back to CPU for Whisper) |
| `DIARIZATION_DEVICE` | `auto` | `auto` / `cuda` / `mps` / `cpu` |

The Streamlit sidebar and `GET /api/health` report `cuda_available`, `whisper_device`, and `diarization_device` so you can confirm acceleration is active.

### CPU PyTorch (default from pip)

`pip install -e ".[diarization]"` typically installs a **CPU-only** torch wheel (`+cpu`). On that build, `torch.cuda.is_available()` is always false even if you have an NVIDIA GPU.

### CUDA PyTorch (NVIDIA GPU)

1. Install a CUDA-capable NVIDIA driver.
2. Reinstall torch/torchaudio with a CUDA build that matches your driver (example for CUDA 12.x — check [pytorch.org](https://pytorch.org/get-started/locally/) for current commands):

```powershell
pip uninstall -y torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124
```

3. Verify:

```powershell
.venv\Scripts\python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

4. Restart the API. Health should show `cuda_available: true` and Whisper/diarization devices as `cuda`.

Keep `WHISPER_DEVICE=auto` and `DIARIZATION_DEVICE=auto` unless you need to force CPU.

### Apple Silicon (MPS)

Diarization can use `mps` when `DIARIZATION_DEVICE=auto` on Mac. Whisper (faster-whisper) stays on CPU unless you set CUDA (not applicable on Apple Silicon).

## Speaker diarization (optional)

When pyannote is installed, audio uploads are automatically split into **Person A / Person B** turns using local speaker diarization.

1. Install optional dependencies:
   ```powershell
   pip install -e ".[diarization]"
   ```
   For GPU acceleration, follow **CUDA PyTorch** above after installing the diarization extra.
2. Accept the model terms on Hugging Face (logged in as the same account as `HF_TOKEN`):
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Add your token to `.env`:
   ```env
   HF_TOKEN=your_huggingface_token
   DIARIZATION_ENABLED=true
   ```

| Variable | Default | Notes |
|----------|---------|-------|
| `DIARIZATION_ENABLED` | `true` | Set `false` to skip diarization |
| `DIARIZATION_MODEL` | `pyannote/speaker-diarization-3.1` | Hugging Face pipeline id |
| `DIARIZATION_DEVICE` | `auto` | Same preference order as Whisper (CUDA → MPS → CPU) |
| `DIARIZATION_SPEAKER_PREFIX` | `Person` | Labels become Person A, Person B, … |
| `DIARIZATION_MIN_SPEAKERS` | _(empty)_ | Default min speakers when no per-upload hint |
| `DIARIZATION_MAX_SPEAKERS` | _(empty)_ | Default max speakers when no per-upload hint |
| `HF_TOKEN` | _(empty)_ | Required for gated pyannote models |

On Windows, pyannote may warn that **torchcodec** is unavailable. The app decodes audio with **ffmpeg/ffprobe** (same tools used for transcription) before running diarization. Ensure both are on `PATH`.

If diarization is unavailable, transcription still works with a single **Speaker 1** label. The sidebar shows **Diarization: Connected** when ready.

Restart the API after changing these settings.

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
