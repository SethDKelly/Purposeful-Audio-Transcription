import os
import tempfile
from pathlib import Path

import pytest

_TEST_DB = Path(tempfile.gettempdir()) / "purposeful_rre_test.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"
os.environ["ALEMBIC_AUTO_UPGRADE"] = "false"
os.environ["API_KEY"] = ""


@pytest.fixture(autouse=True)
def reset_db() -> None:
    from backend.db.base import Base, engine, init_db

    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
