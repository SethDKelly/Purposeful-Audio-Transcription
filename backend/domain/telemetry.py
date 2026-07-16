"""LLM / module-run telemetry helpers (v0.7 P6)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_write_input_tokens: int = 0
    latency_ms: int = 0

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class ModuleRunTelemetry:
    model: str | None = None
    latency_ms: int = 0
    retry_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_write_input_tokens: int = 0
    estimated_cost_usd: float = 0.0
    finding_count: int = 0
    construct_count: int = 0
    relationship_count: int = 0
    evidence_quote_count: int = 0
    validation_failure_count: int = 0
    coverage_rate: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def estimate_cost_usd(
    *,
    input_tokens: int,
    output_tokens: int,
    cache_read_input_tokens: int = 0,
    cache_write_input_tokens: int = 0,
    input_per_mtok: float,
    output_per_mtok: float,
    cache_read_per_mtok: float,
    cache_write_per_mtok: float,
) -> float:
    """Estimate USD cost from token counts and per-million-token rates."""
    cost = (
        (input_tokens / 1_000_000) * input_per_mtok
        + (output_tokens / 1_000_000) * output_per_mtok
        + (cache_read_input_tokens / 1_000_000) * cache_read_per_mtok
        + (cache_write_input_tokens / 1_000_000) * cache_write_per_mtok
    )
    return round(cost, 6)


def aggregate_workflow_telemetry(module_telemetries: list[dict[str, Any]]) -> dict[str, Any]:
    total_latency = 0
    total_cost = 0.0
    total_input = 0
    total_output = 0
    total_retries = 0
    total_findings = 0
    total_constructs = 0
    for item in module_telemetries:
        total_latency += int(item.get("latency_ms") or 0)
        total_cost += float(item.get("estimated_cost_usd") or 0.0)
        total_input += int(item.get("input_tokens") or 0)
        total_output += int(item.get("output_tokens") or 0)
        total_retries += int(item.get("retry_count") or 0)
        total_findings += int(item.get("finding_count") or 0)
        total_constructs += int(item.get("construct_count") or 0)
    return {
        "module_count": len(module_telemetries),
        "total_latency_ms": total_latency,
        "total_estimated_cost_usd": round(total_cost, 6),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_retries": total_retries,
        "total_findings": total_findings,
        "total_constructs": total_constructs,
        "modules": module_telemetries,
    }
