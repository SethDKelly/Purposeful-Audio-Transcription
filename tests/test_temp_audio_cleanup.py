"""Temp upload lifecycle — P1-3a."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.services.audio_service import saved_upload


def test_saved_upload_deletes_temp_file_on_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("backend.services.audio_service.settings.temp_dir", tmp_path)
    with saved_upload(b"audio-bytes", "sample.wav") as path:
        assert path.exists()
        assert path.parent == tmp_path
        assert path.read_bytes() == b"audio-bytes"
    assert not path.exists()
    assert list(tmp_path.iterdir()) == []


def test_saved_upload_deletes_temp_file_on_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("backend.services.audio_service.settings.temp_dir", tmp_path)
    leaked: Path | None = None
    with pytest.raises(RuntimeError, match="boom"):
        with saved_upload(b"x", "fail.mp3") as path:
            leaked = path
            assert path.exists()
            raise RuntimeError("boom")
    assert leaked is not None
    assert not leaked.exists()
