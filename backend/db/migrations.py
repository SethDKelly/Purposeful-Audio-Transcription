from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

_ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def upgrade_head() -> None:
    config = _alembic_config()
    _repair_alembic_version_if_needed(config)
    command.upgrade(config, "head")


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
