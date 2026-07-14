import os
import tempfile
import warnings
from pathlib import Path

import pytest

_TEST_DB = Path(tempfile.gettempdir()) / "purposeful_rre_test.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"
os.environ["ALEMBIC_AUTO_UPGRADE"] = "false"
os.environ["API_KEY"] = ""

# pyannote warns when torchcodec cannot load FFmpeg libs; RRE decodes via ffmpeg CLI.
warnings.filterwarnings(
    "ignore",
    message=".*torchcodec is not installed correctly.*",
    category=UserWarning,
    module=r"pyannote\.audio\.core\.io",
)


@pytest.fixture(autouse=True)
def reset_db() -> None:
    from backend.db.base import Base, engine, init_db

    init_db()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
