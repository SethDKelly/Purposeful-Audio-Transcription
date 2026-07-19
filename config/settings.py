from pathlib import Path

from pydantic import AliasChoices, Field
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
    # Lean structured JSON; long raw_markdown_report is discouraged in prompts.
    bedrock_max_tokens: int = 8192
    bedrock_structured_output: bool = True
    # Cache shared framework (+ transcript evidence prefix) across modules in a run.
    bedrock_prompt_cache: bool = True
    # Sonnet 4.5 supports 5m and 1h; 1h fits long suite waves.
    bedrock_prompt_cache_ttl: str = "1h"
    # Approximate Bedrock Sonnet rates (USD per 1M tokens) for telemetry estimates.
    bedrock_input_cost_per_mtok: float = 3.0
    bedrock_output_cost_per_mtok: float = 15.0
    bedrock_cache_read_cost_per_mtok: float = 0.30
    bedrock_cache_write_cost_per_mtok: float = 3.75
    aws_region: str = ""
    uploads_bucket: str = ""
    transcribe_language: str = ""
    transcribe_max_speakers: int = 10
    transcribe_poll_seconds: float = 5.0
    transcribe_timeout_seconds: float = 3600.0
    speaker_prefix: str = "Person"
    max_upload_mb: int = 100
    temp_dir: Path = Path("./data/temp")
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    # Preferred env: RRE_API_BASE_URL. BACKEND_API_URL accepted for React-readiness docs.
    rre_api_base_url: str = Field(
        default="",
        validation_alias=AliasChoices(
            "RRE_API_BASE_URL",
            "BACKEND_API_URL",
            "rre_api_base_url",
        ),
    )
    streamlit_port: int = 8501
    prompts_dir: Path = Path("./config/prompts")
    modules_dir: Path = Path("./config/modules")
    framework_dir: Path = Path("./config/framework")
    workflows_dir: Path = Path("./config/workflows")
    ontology_dir: Path = Path("./config/ontology")
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
    # Parallel transcript modules within a workflow (meta-synthesis stays sequential).
    # Capped to limit Bedrock TPS / API load; SQLite forces 1 in the engine.
    workflow_module_concurrency: int = 3
    # Dedicated worker polls CREATED jobs when true; API does not run them inline.
    workflow_worker_enabled: bool = False
    workflow_worker_poll_seconds: float = 2.0
    # Max CREATED jobs to claim in one poll_once() cycle.
    workflow_worker_max_claim_per_poll: int = 1
    # Max concurrent workflow jobs on a single worker process.
    workflow_worker_max_in_flight: int = 2
    # Local HTTP health port for ECS container checks (worker process only).
    workflow_worker_health_port: int = 8080
    # Wall-clock timeout for a single workflow job attempt (0 = disabled).
    workflow_job_timeout_seconds: float = 7200.0
    # Requeue failed attempts up to this count (includes the first try).
    workflow_job_max_attempts: int = 2
    # Requeue/fail RUNNING jobs abandoned after worker crash (seconds since claim).
    workflow_job_stale_seconds: float = 7800.0
    # One repair attempt (2 Converse calls total) after structured-output hardening.
    module_run_max_retries: int = 1
    # Bedrock ThrottlingException / TooManyRequests backoff.
    bedrock_throttle_max_retries: int = 5
    bedrock_throttle_base_seconds: float = 2.0
    evidence_prompt_max_quotes: int = 120
    evidence_prompt_head_quotes: int = 80
    evidence_prompt_tail_quotes: int = 40
    transcript_retention_days: int | None = None
    # Pytest-only convenience: auto-approve transcripts when workflows start.
    # Never enable on AWS ECS.
    auto_mark_transcript_ready: bool = False

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
