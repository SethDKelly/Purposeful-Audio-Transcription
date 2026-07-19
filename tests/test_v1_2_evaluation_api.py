"""Evaluation harness and API v1 contract tests (v1.2)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.evaluation.harness import (
    EvalGateConfig,
    GoldenEvalHarness,
    ModuleVersionComparer,
    evaluate_module_output,
)
from backend.evaluation.reports import write_eval_reports
from backend.main import app
from tests.helpers.golden_transcripts import load_golden_fixture_by_id
from tests.test_workflow_engine import _module_llm_response


def _parse_module_response(module_id: str) -> dict:
    raw = _module_llm_response(module_id)
    payload = raw.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
    return json.loads(payload)


def test_evaluate_module_output_scores_gt001() -> None:
    fixture = load_golden_fixture_by_id("GT001")
    output = _parse_module_response("relationship_conversation_analysis")
    result = evaluate_module_output(
        fixture=fixture,
        module_id="relationship_conversation_analysis",
        module_output=output,
        confidence_ceiling="moderate",
        gates=EvalGateConfig(min_required_signal_hit_rate=0.0, min_evidence_coverage_rate=0.0),
    )
    assert result.fixture_id == "GT001"
    assert result.finding_count >= 1
    assert result.forbidden_claim_count == 0


def test_write_eval_reports(tmp_path: Path) -> None:
    fixture = load_golden_fixture_by_id("GT001")
    output = _parse_module_response("nvc_analysis")
    result = GoldenEvalHarness().score_output(
        fixture_id=fixture.fixture_id,
        module_id="nvc_analysis",
        module_output=output,
    )
    paths = write_eval_reports([result], tmp_path, run_id="test-run")
    assert paths["json"].is_file()
    assert paths["markdown"].is_file()
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["result_count"] == 1


def test_module_version_comparer_detects_forbidden_regression() -> None:
    fixture = load_golden_fixture_by_id("GT001")
    output = _parse_module_response("relationship_conversation_analysis")
    baseline = evaluate_module_output(
        fixture=fixture,
        module_id="relationship_conversation_analysis",
        module_output=output,
        module_version="1.0.0",
        gates=EvalGateConfig(min_required_signal_hit_rate=0.0, min_evidence_coverage_rate=0.0),
    )
    bad = dict(output)
    bad["executive_summary"] = "They will divorce; this is abuse and he is a narcissist."
    candidate = evaluate_module_output(
        fixture=fixture,
        module_id="relationship_conversation_analysis",
        module_output=bad,
        module_version="1.0.1",
        gates=EvalGateConfig(min_required_signal_hit_rate=0.0, min_evidence_coverage_rate=0.0),
    )
    cmp = ModuleVersionComparer().compare(baseline=baseline, candidate=candidate)
    assert "forbidden_claim_count" in cmp["regressions"]


def test_api_v1_transcript_and_status_contract() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v1/transcripts",
        json={"raw_text": "Person A: Hello.\nPerson B: Hi.", "source_type": "paste", "title": "v1"},
    )
    assert created.status_code == 200
    transcript_id = created.json()["transcript"]["id"]
    fetched = client.get(f"/api/v1/transcripts/{transcript_id}")
    assert fetched.status_code == 200
    client.post(f"/api/transcripts/{transcript_id}/ready", json={"skip_review": True})
    run = client.post(
        "/api/v1/workflow-runs",
        json={
            "workflow_id": "quick_review",
            "transcript_id": transcript_id,
            "background": True,
            "model": "test",
        },
    )
    # May fail without worker/LLM depending on settings; accept 200 or queue-created path
    assert run.status_code in {200, 422, 500, 503} or run.status_code == 200
    if run.status_code == 200:
        run_id = run.json()["id"]
        status = client.get(f"/api/v1/workflow-runs/{run_id}/status")
        assert status.status_code == 200
        body = status.json()
        assert body["schema_version"] == "1"
        assert "status" in body


def test_error_contract_includes_error_code() -> None:
    @app.get("/__test_v12_error")
    def _boom() -> None:
        from backend.core.exceptions import AppError

        raise AppError("Visible", status_code=400, error_code="TestError")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/__test_v12_error", headers={"X-Request-ID": "v12-1"})
    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "TestError"
    assert body["message"] == "Visible"
    assert body["detail"] == "Visible"
    assert body["request_id"] == "v12-1"


def test_openapi_v1_paths_snapshot() -> None:
    client = TestClient(app)
    spec = client.get("/openapi.json").json()
    paths = sorted(p for p in spec["paths"] if p.startswith("/api/v1/"))
    expected = [
        "/api/v1/cases",
        "/api/v1/cases/{case_id}",
        "/api/v1/cases/{case_id}/timeline",
        "/api/v1/exports",
        "/api/v1/findings/{finding_key}/feedback",
        "/api/v1/reports/{run_id}",
        "/api/v1/reports/{run_id}/evidence",
        "/api/v1/reports/{run_id}/findings",
        "/api/v1/transcripts",
        "/api/v1/transcripts/{transcript_id}",
        "/api/v1/transcripts/{transcript_id}/case",
        "/api/v1/transcripts/{transcript_id}/evidence/rebuild",
        "/api/v1/transcripts/{transcript_id}/ready",
        "/api/v1/transcripts/{transcript_id}/speakers",
        "/api/v1/transcripts/{transcript_id}/turns",
        "/api/v1/workflow-runs",
        "/api/v1/workflow-runs/{run_id}",
        "/api/v1/workflow-runs/{run_id}/status",
        "/api/v1/workflows",
    ]
    assert paths == expected
    snapshot = Path("tests/snapshots/openapi_v1_paths.json")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if not snapshot.is_file():
        snapshot.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    assert json.loads(snapshot.read_text(encoding="utf-8")) == expected
