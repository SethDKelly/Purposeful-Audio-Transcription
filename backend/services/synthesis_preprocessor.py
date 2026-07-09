"""Pre-process module outputs for synthesis."""

from dataclasses import dataclass, field

from backend.domain.enums import Confidence
from backend.domain.finding import ModuleRun

META_SYNTHESIS_MODULE_ID = "meta_synthesis"

_HIGH_CONFIDENCE = {Confidence.OBSERVED, Confidence.HIGH}
_MODERATE_CONFIDENCE = {Confidence.MODERATE}
_EXPLORATORY_CONFIDENCE = {
    Confidence.LOW,
    Confidence.EXPLORATORY,
    Confidence.INSUFFICIENT_EVIDENCE,
}


@dataclass(frozen=True)
class IndexedFinding:
    module_id: str
    module_run_id: str
    finding_id: str
    finding_type: str
    title: str
    summary: str
    confidence: str
    evidence_quote_ids: tuple[str, ...]


@dataclass
class SynthesisPreprocessResult:
    findings_by_type: dict[str, list[IndexedFinding]] = field(default_factory=dict)
    convergence: list[str] = field(default_factory=list)
    divergence: list[str] = field(default_factory=list)
    module_summaries: dict[str, str] = field(default_factory=dict)
    allowed_quote_ids: set[str] = field(default_factory=set)
    source_module_run_ids: list[str] = field(default_factory=list)


class SynthesisPreprocessor:
    def process(self, module_runs: list[ModuleRun]) -> SynthesisPreprocessResult:
        result = SynthesisPreprocessResult()
        indexed_findings: list[IndexedFinding] = []

        for module_run in module_runs:
            if module_run.module_id == META_SYNTHESIS_MODULE_ID:
                continue
            if module_run.status != "completed" or not module_run.parsed_output:
                continue

            result.source_module_run_ids.append(module_run.id)
            output = module_run.parsed_output
            result.module_summaries[module_run.module_id] = output.get(
                "executive_summary", ""
            )

            for finding in output.get("findings", []):
                quote_ids = tuple(finding.get("evidence_quote_ids", []))
                result.allowed_quote_ids.update(quote_ids)
                indexed = IndexedFinding(
                    module_id=module_run.module_id,
                    module_run_id=module_run.id,
                    finding_id=finding.get("id", ""),
                    finding_type=str(finding.get("type", "observation")),
                    title=str(finding.get("title", "")).strip(),
                    summary=str(finding.get("summary", "")).strip(),
                    confidence=str(finding.get("confidence", "moderate")),
                    evidence_quote_ids=quote_ids,
                )
                indexed_findings.append(indexed)
                result.findings_by_type.setdefault(indexed.finding_type, []).append(
                    indexed
                )

        result.convergence = self._detect_convergence(indexed_findings)
        result.divergence = self._detect_divergence(indexed_findings)
        return result

    def _detect_convergence(self, findings: list[IndexedFinding]) -> list[str]:
        statements: list[str] = []
        seen_pairs: set[tuple[str, str, str]] = set()

        for left_index, left in enumerate(findings):
            for right in findings[left_index + 1 :]:
                if left.module_id == right.module_id:
                    continue
                shared = set(left.evidence_quote_ids) & set(right.evidence_quote_ids)
                if not shared:
                    continue

                pair_key = (
                    left.module_id,
                    right.module_id,
                    ",".join(sorted(shared)),
                )
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                quotes = ", ".join(sorted(shared))
                statements.append(
                    f"Modules {left.module_id} and {right.module_id} both support "
                    f"{left.finding_type.replace('_', ' ')} themes with shared evidence "
                    f"({quotes}): '{left.title}' and '{right.title}'."
                )
        return statements

    def _detect_divergence(self, findings: list[IndexedFinding]) -> list[str]:
        statements: list[str] = []
        seen_pairs: set[tuple[str, str, str]] = set()

        for left_index, left in enumerate(findings):
            for right in findings[left_index + 1 :]:
                if left.module_id == right.module_id:
                    continue
                if left.finding_type != right.finding_type:
                    continue
                if set(left.evidence_quote_ids) & set(right.evidence_quote_ids):
                    continue

                pair_key = (left.module_id, right.module_id, left.finding_type)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                statements.append(
                    f"Modules {left.module_id} and {right.module_id} emphasize different "
                    f"{left.finding_type.replace('_', ' ')} lenses: "
                    f"'{left.title}' vs '{right.title}'."
                )
        return statements


synthesis_preprocessor = SynthesisPreprocessor()
