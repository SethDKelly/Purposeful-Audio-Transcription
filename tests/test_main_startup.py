from unittest.mock import MagicMock, patch

from backend.main import _acquire_startup_leader, _release_startup_leader


@patch("backend.main.settings")
def test_startup_leader_always_true_on_sqlite(mock_settings) -> None:
    mock_settings.is_sqlite = True
    assert _acquire_startup_leader() is True
    _release_startup_leader()


@patch("backend.main.engine")
@patch("backend.main.settings")
def test_startup_leader_uses_advisory_lock(mock_settings, mock_engine) -> None:
    mock_settings.is_sqlite = False
    conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = conn
    conn.execute.return_value.scalar.return_value = True

    assert _acquire_startup_leader() is True
    conn.execute.assert_called()
    _release_startup_leader()
