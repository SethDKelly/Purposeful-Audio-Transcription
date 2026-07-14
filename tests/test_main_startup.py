from unittest.mock import MagicMock, patch

from backend.main import _acquire_startup_leader, _release_startup_leader, _wait_for_database


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


@patch("backend.main.engine")
@patch("backend.main.settings")
def test_startup_leader_fails_closed_on_lock_error(mock_settings, mock_engine) -> None:
    mock_settings.is_sqlite = False
    mock_engine.connect.side_effect = RuntimeError("db down")
    assert _acquire_startup_leader() is False


@patch("backend.main.engine")
def test_wait_for_database_returns_false_on_timeout(mock_engine) -> None:
    mock_engine.connect.side_effect = RuntimeError("db down")
    assert _wait_for_database(timeout_seconds=0.05) is False
