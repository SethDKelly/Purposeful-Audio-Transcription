from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


@patch("backend.api.routes.analyze.analysis_service.analyze")
def test_analyze_endpoint_returns_deprecation_headers(mock_analyze) -> None:
    mock_analyze.return_value = {
        "purpose_id": "relationship_conversation_analysis",
        "purpose_name": "Relationship Conversation Analysis",
        "model": "test-model",
        "analysis": "Test report",
    }

    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "transcript": "Person A: Hello.",
            "purpose_id": "relationship_conversation_analysis",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("Deprecation") == "true"
    assert "workflows" in response.headers.get("Link", "")
    assert "deprecated" in response.headers.get("X-Deprecated-Endpoint", "").lower()


@patch("backend.api.routes.analyze.analysis_service.analyze_stream")
def test_analyze_stream_endpoint_is_not_deprecated(mock_stream) -> None:
    mock_stream.return_value = iter(["chunk"])
    client = TestClient(app)
    response = client.post(
        "/api/analyze/stream",
        json={
            "transcript": "Person A: Hello.",
            "purpose_id": "relationship_conversation_analysis",
        },
    )

    assert response.status_code != 404
    assert response.headers.get("Deprecation") is None
