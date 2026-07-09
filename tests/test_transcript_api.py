from fastapi.testclient import TestClient

from backend.main import app


def test_create_and_get_transcript() -> None:
    client = TestClient(app)
    payload = {
        "raw_text": "Person A: Hello there.\nPerson B: Hi back.",
        "source_type": "paste",
        "title": "Test conversation",
    }
    create_response = client.post("/api/transcripts", json=payload)
    assert create_response.status_code == 200
    data = create_response.json()
    assert data["transcript"]["title"] == "Test conversation"
    assert len(data["speakers"]) == 2
    assert len(data["turns"]) == 2
    assert data["evidence_quotes"][0]["quote_id"] == "Q001"

    transcript_id = data["transcript"]["id"]
    get_response = client.get(f"/api/transcripts/{transcript_id}")
    assert get_response.status_code == 200
    assert get_response.json()["evidence_quotes"][1]["quote_id"] == "Q002"


def test_update_speakers() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/transcripts",
        json={"raw_text": "Person A: Hello.", "source_type": "paste"},
    )
    data = create_response.json()
    transcript_id = data["transcript"]["id"]
    speaker_id = data["speakers"][0]["id"]

    patch_response = client.patch(
        f"/api/transcripts/{transcript_id}/speakers",
        json={"speakers": [{"id": speaker_id, "display_name": "Alex"}]},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["speakers"][0]["display_name"] == "Alex"
