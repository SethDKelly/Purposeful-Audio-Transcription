from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


@patch("backend.api.routes.module_stream.module_runner.stream_for_transcript_text")
def test_module_stream_endpoint_returns_tokens(mock_stream) -> None:
    mock_stream.return_value = iter(["chunk-1", "chunk-2"])

    client = TestClient(app)
    response = client.post(
        "/api/modules/relationship_conversation_analysis/stream",
        json={"transcript": "Person A: Hello."},
    )

    assert response.status_code == 200
    assert response.text == "chunk-1chunk-2"
    mock_stream.assert_called_once()


def test_analyze_endpoint_removed() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "transcript": "Person A: Hello.",
            "purpose_id": "relationship_conversation_analysis",
        },
    )
    assert response.status_code == 404


def test_purposes_endpoint_is_deprecated_alias() -> None:
    client = TestClient(app)
    response = client.get("/api/purposes")
    assert response.status_code == 200
    assert response.headers.get("Deprecation") == "true"
    assert len(response.json()["purposes"]) == 14
