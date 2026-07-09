from pathlib import Path

from alembic import command
from alembic.config import Config

_ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def upgrade_head() -> None:
    command.upgrade(_alembic_config(), "head")


def _alembic_config() -> Config:
    config = Config(str(_ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", _get_settings().database_url)
    return config


def _get_settings():
    from config.settings import settings

    return settings
