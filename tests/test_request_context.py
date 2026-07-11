from fastapi.testclient import TestClient

from backend.main import app


def test_request_id_header_is_returned() -> None:
    client = TestClient(app)
    response = client.get("/api/health", headers={"X-Request-ID": "test-request-123"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "test-request-123"


def test_request_id_is_generated_when_missing() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert len(request_id) >= 32
