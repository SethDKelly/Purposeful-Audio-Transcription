import os
import tempfile
from pathlib import Path

import pytest

from tests.helpers.golden_transcripts import iter_golden_fixtures, load_golden_fixture_by_id

_TEST_DB = Path(tempfile.gettempdir()) / "purposeful_rre_test.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"
os.environ["ALEMBIC_AUTO_UPGRADE"] = "false"
os.environ["API_KEY"] = ""
os.environ["AUTO_MARK_TRANSCRIPT_READY"] = "true"


@pytest.fixture(autouse=True)
def reset_db() -> None:
    from backend.db.base import Base, engine, init_db

    Base.metadata.drop_all(bind=engine)
    init_db()
    yield


@pytest.fixture(params=iter_golden_fixtures(), ids=lambda fixture: fixture.path.name)
def golden_fixture(request):
    return request.param


@pytest.fixture
def gt001_fixture():
    return load_golden_fixture_by_id("GT001")


@pytest.fixture
def gt002_fixture():
    return load_golden_fixture_by_id("GT002")
