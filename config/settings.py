from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AWS product defaults (ECS). pytest overrides DB via conftest.
    llm_provider: str = "bedrock"
    transcription_provider: str = "transcribe"
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    bedrock_max_tokens: int = 8192
    aws_region: str = ""
    uploads_bucket: str = ""
    transcribe_language: str = ""
    transcribe_max_speakers: int = 10
    transcribe_poll_seconds: float = 5.0
    transcribe_timeout_seconds: float = 600.0
    speaker_prefix: str = "Person"
    max_upload_mb: int = 100
    temp_dir: Path = Path("./data/temp")
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    rre_api_base_url: str = ""
    streamlit_port: int = 8501
    prompts_dir: Path = Path("./config/prompts")
    modules_dir: Path = Path("./config/modules")
    framework_dir: Path = Path("./config/framework")
    workflows_dir: Path = Path("./config/workflows")
    # Legacy alias accepted for module/model resolution when BEDROCK default unused.
    default_ollama_model: str = ""
    database_url: str = "sqlite:///./data/rre.db"
    database_pool_size: int = 5
    alembic_auto_upgrade: bool = False
    api_key: str = ""
    log_json: bool = False
    log_redact: bool | None = None
    workflow_background_default: bool = False
    workflow_sync_module_limit: int = 6
    module_run_max_retries: int = 2
    evidence_prompt_max_quotes: int = 120
    evidence_prompt_head_quotes: int = 80
    evidence_prompt_tail_quotes: int = 40
    transcript_retention_days: int | None = None

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

    @property
    def api_base_url(self) -> str:
        if self.rre_api_base_url.strip():
            return self.rre_api_base_url.rstrip("/")
        return f"http://{self.api_host}:{self.api_port}"

    @property
    def resolved_aws_region(self) -> str:
        import os

        return (self.aws_region or os.environ.get("AWS_REGION") or "us-east-2").strip()

    @property
    def resolved_bedrock_model_id(self) -> str:
        return self.bedrock_model_id.strip()

    @property
    def log_redaction_enabled(self) -> bool:
        if self.log_redact is not None:
            return self.log_redact
        return True

    @property
    def default_llm_model(self) -> str:
        return self.resolved_bedrock_model_id or self.default_ollama_model


settings = Settings()
