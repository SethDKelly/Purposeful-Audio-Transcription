from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs() -> dict:
    if settings.is_sqlite:
        return {"connect_args": {"check_same_thread": False}}
    return {
        "pool_pre_ping": True,
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_pool_size,
    }


engine = create_engine(settings.database_url, **_engine_kwargs())
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from backend.db import models  # noqa: F401

    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    if settings.is_sqlite:
        db_path_parent = settings.database_url.replace("sqlite:///", "")
        if db_path_parent and not db_path_parent.startswith(":"):
            Path(db_path_parent).parent.mkdir(parents=True, exist_ok=True)

    if settings.alembic_auto_upgrade:
        from backend.db.migrations import upgrade_head

        upgrade_head()
    else:
        Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
