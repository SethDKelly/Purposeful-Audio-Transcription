from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_host: str = "http://localhost:11434"
    whisper_model: str = "base"
    whisper_device: str = "auto"
    whisper_compute_type: str = "int8"
    diarization_enabled: bool = True
    diarization_model: str = "pyannote/speaker-diarization-3.1"
    diarization_device: str = "auto"
    diarization_speaker_prefix: str = "Person"
    diarization_min_speakers: int | None = None
    diarization_max_speakers: int | None = None
    # Drop speaker turns shorter than this (seconds); absorbs into neighbors.
    diarization_min_duration_on: float = 0.3
    # Merge same-speaker intervals separated by gaps shorter than this (seconds).
    diarization_min_duration_off: float = 0.2
    hf_token: str = ""
    transcription_mode: str = "sliced"
    whisper_min_slice_duration: float = 0.5
    whisper_batch_size: int = 8
    whisper_max_slices: int = 200
    max_upload_mb: int = 100
    temp_dir: Path = Path("./data/temp")
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    streamlit_port: int = 8501
    prompts_dir: Path = Path("./config/prompts")
    modules_dir: Path = Path("./config/modules")
    framework_dir: Path = Path("./config/framework")
    workflows_dir: Path = Path("./config/workflows")
    default_ollama_model: str = ""
    # Disable Ollama "thinking" mode for structured JSON module output (Gemma 4 etc.).
    ollama_think: bool = False
    database_url: str = "sqlite:///./data/rre.db"
    database_pool_size: int = 5
    alembic_auto_upgrade: bool = False
    api_key: str = ""
    log_json: bool = False
    workflow_background_default: bool = False
    module_run_max_retries: int = 2
    evidence_prompt_max_quotes: int = 120
    evidence_prompt_head_quotes: int = 80
    evidence_prompt_tail_quotes: int = 40

    allowed_extensions: frozenset[str] = frozenset(
        {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm", ".mp4"}
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def api_auth_enabled(self) -> bool:
        return bool(self.api_key)


settings = Settings()
