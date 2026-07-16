"""API key auth for UI→API (V07-1b)."""

from fastapi.testclient import TestClient

from backend.main import app
from config.settings import settings


def test_api_key_required_when_configured(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "test-secret-key")
    client = TestClient(app)
    denied = client.get("/api/workflows")
    assert denied.status_code == 401

    allowed = client.get(
        "/api/workflows",
        headers={"X-API-Key": "test-secret-key"},
    )
    assert allowed.status_code == 200


def test_live_remains_public_when_api_key_configured(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "test-secret-key")
    client = TestClient(app)
    response = client.get("/api/live")
    assert response.status_code == 200
