from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

_ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def upgrade_head() -> None:
    config = _alembic_config()
    settings = _get_settings()
    if not settings.is_sqlite:
        from backend.db.base import engine

        _ensure_alembic_version_column_width(engine)
    _repair_alembic_version_if_needed(config)
    command.upgrade(config, "head")


def _ensure_alembic_version_column_width(engine) -> None:  # noqa: ANN001
    """Alembic defaults to version_num VARCHAR(32); some revision ids are longer."""
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT character_maximum_length FROM information_schema.columns "
                "WHERE table_name = 'alembic_version' AND column_name = 'version_num'"
            )
        ).first()
        if row is None:
            return
        max_len = row[0]
        if max_len is not None and max_len < 128:
            conn.execute(
                text(
                    "ALTER TABLE alembic_version "
                    "ALTER COLUMN version_num TYPE VARCHAR(128)"
                )
            )
            conn.commit()


def _repair_alembic_version_if_needed(config: Config) -> None:
    """Align alembic_version when schema objects exist but revision is behind."""
    settings = _get_settings()
    if settings.is_sqlite:
        return

    from backend.db.base import engine

    insp = inspect(engine)
    tables = set(insp.get_table_names())
    with engine.connect() as conn:
        row = conn.execute(text("SELECT version_num FROM alembic_version")).first()
    if row is None:
        return
    current = row[0]

    if current == "011_safety_mode" and {"safety_events", "evaluation_runs"}.issubset(tables):
        command.stamp(config, "012_safety_events_evaluation_runs")


def _alembic_config() -> Config:
    config = Config(str(_ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", _get_settings().database_url)
    return config


def _get_settings():
    from config.settings import settings

    return settings
