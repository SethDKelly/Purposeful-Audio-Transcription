from collections.abc import Callable
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

_ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"

# Revisions that may be ahead of alembic_version when RDS schema drifted.
_DRIFT_CHECK_REVISIONS = (
    "012_safety_events_evaluation_runs",
    "013_email_auth_and_ownership",
    "014_evidence_precision",
    "015_evidence_snapshots_and_versioning",
    "016_relationship_evidence_fields",
)


def upgrade_head() -> None:
    config = _alembic_config()
    settings = _get_settings()
    if not settings.is_sqlite:
        from backend.db.base import engine

        _ensure_alembic_version_column_width(engine)
        _reconcile_alembic_version_if_needed(config, engine)
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


def _schema_satisfies_revision(
    revision: str,
    tables: set[str],
    has_column: Callable[[str, str], bool],
) -> bool:
    if revision == "012_safety_events_evaluation_runs":
        return {"safety_events", "evaluation_runs"}.issubset(tables)
    if revision == "013_email_auth_and_ownership":
        return "users" in tables and has_column("workflow_runs", "owner_user_id")
    if revision == "014_evidence_precision":
        return has_column("evidence_quotes", "evidence_type")
    if revision == "015_evidence_snapshots_and_versioning":
        return "transcript_versions" in tables and has_column(
            "workflow_runs", "transcript_version_id"
        )
    if revision == "016_relationship_evidence_fields":
        return has_column("construct_relationships", "rationale")
    return False


def _reconcile_alembic_version_if_needed(config: Config, engine) -> None:  # noqa: ANN001
    """Stamp alembic_version forward when schema objects exist but revision is behind."""
    insp = inspect(engine)
    tables = set(insp.get_table_names())

    def has_column(table: str, column: str) -> bool:
        if table not in tables:
            return False
        cols = {c["name"] for c in insp.get_columns(table)}
        return column in cols

    with engine.connect() as conn:
        row = conn.execute(text("SELECT version_num FROM alembic_version")).first()
    if row is None:
        return
    current = row[0]

    script = ScriptDirectory.from_config(config)
    ordered: list[str] = []
    rev = script.get_revision("017_seed_admin_user")
    while rev is not None:
        ordered.append(rev.revision)
        down = rev.down_revision
        if down is None:
            break
        down_id = down[0] if isinstance(down, tuple) else down
        rev = script.get_revision(down_id)
    ordered.reverse()

    if current not in ordered:
        return

    current_idx = ordered.index(current)
    effective_idx = current_idx
    for candidate in _DRIFT_CHECK_REVISIONS:
        if candidate not in ordered:
            continue
        if not _schema_satisfies_revision(candidate, tables, has_column):
            continue
        idx = ordered.index(candidate)
        if idx > effective_idx:
            effective_idx = idx

    if effective_idx > current_idx:
        command.stamp(config, ordered[effective_idx])


def _alembic_config() -> Config:
    config = Config(str(_ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", _get_settings().database_url)
    return config


def _get_settings():
    from config.settings import settings

    return settings
