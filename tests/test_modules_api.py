from fastapi.testclient import TestClient

from backend.main import app


def test_list_modules_api() -> None:
    client = TestClient(app)
    response = client.get("/api/modules")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload["modules"]) == 5

    module = next(
        item for item in payload["modules"] if item["id"] == "relationship_conversation_analysis"
    )
    assert module["name"] == "Relationship Conversation Analysis"
    assert module["output_schema"] == "module_output_v1"
    assert module["input_type"] == "transcript"


def test_list_purposes_still_works() -> None:
    client = TestClient(app)
    response = client.get("/api/purposes")
    assert response.status_code == 200
    assert len(response.json()["purposes"]) >= 5
