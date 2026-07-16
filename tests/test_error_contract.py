"""API error contract: generic 500s and request_id correlation."""

from fastapi.testclient import TestClient

from backend.core.exceptions import AppError
from backend.main import app


def test_app_error_includes_request_id() -> None:
    @app.get("/__test_app_error")
    def _boom() -> None:
        raise AppError("Visible client message", status_code=400)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/__test_app_error",
        headers={"X-Request-ID": "err-req-1"},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Visible client message"
    assert body["request_id"] == "err-req-1"
    assert response.headers.get("X-Request-ID") == "err-req-1"


def test_unhandled_error_hides_exception_details() -> None:
    @app.get("/__test_unhandled")
    def _boom() -> None:
        raise RuntimeError("secret internals should not leak")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/__test_unhandled",
        headers={"X-Request-ID": "err-req-2"},
    )
    assert response.status_code == 500
    body = response.json()
    assert "secret internals" not in body["detail"]
    assert "RuntimeError" not in body["detail"]
    assert body.get("request_id") == "err-req-2"
    assert "request id" in body["detail"].lower()
