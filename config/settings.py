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
    max_upload_mb: int = 100
    temp_dir: Path = Path("./data/temp")
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    streamlit_port: int = 8501
    prompts_dir: Path = Path("./config/prompts")
    purposes_file: Path = Path("./config/purposes.yaml")
    default_ollama_model: str = ""

    allowed_extensions: frozenset[str] = frozenset(
        {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm", ".mp4"}
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
