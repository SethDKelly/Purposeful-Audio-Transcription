"""Telemetry helpers and module-run cost estimation."""

from backend.domain.telemetry import aggregate_workflow_telemetry, estimate_cost_usd


def test_estimate_cost_usd_scales_with_tokens() -> None:
    cost = estimate_cost_usd(
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        input_per_mtok=3.0,
        output_per_mtok=15.0,
        cache_read_per_mtok=0.3,
        cache_write_per_mtok=3.75,
    )
    assert cost == 18.0


def test_aggregate_workflow_telemetry() -> None:
    summary = aggregate_workflow_telemetry(
        [
            {
                "latency_ms": 100,
                "estimated_cost_usd": 0.01,
                "input_tokens": 10,
                "output_tokens": 5,
                "retry_count": 0,
                "finding_count": 2,
                "construct_count": 1,
            },
            {
                "latency_ms": 50,
                "estimated_cost_usd": 0.02,
                "input_tokens": 20,
                "output_tokens": 8,
                "retry_count": 1,
                "finding_count": 3,
                "construct_count": 2,
            },
        ]
    )
    assert summary["module_count"] == 2
    assert summary["total_latency_ms"] == 150
    assert summary["total_estimated_cost_usd"] == 0.03
    assert summary["total_retries"] == 1
    assert summary["total_findings"] == 5
