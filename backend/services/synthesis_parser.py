"""Parse and normalize synthesis output into SynthesisReport."""

import uuid
from typing import Any

from pydantic import ValidationError

from backend.domain.enums import Confidence, FindingType
from backend.domain.finding import Finding
from backend.domain.synthesis import SynthesisReport
from backend.schemas.module_output_v1 import FindingInput
from backend.schemas.synthesis_output_v1 import SynthesisOutputInput
from backend.services.output_parser import OutputParseError, _coerce_enum
from backend.services.synthesis_preprocessor import (
    META_SYNTHESIS_MODULE_ID,
    SynthesisPreprocessResult,
    _HIGH_CONFIDENCE,
    _MODERATE_CONFIDENCE,
)


class SynthesisParser:
    def parse_meta_module_output(
        self,
        data: dict[str, Any],
        *,
        workflow_run_id: str,
        synthesis_id: str,
        module_run_id: str,
        preprocessed: SynthesisPreprocessResult,
    ) -> SynthesisReport:
        if _is_synthesis_output_shape(data):
            return self._from_synthesis_output(
                data,
                workflow_run_id=workflow_run_id,
                synthesis_id=synthesis_id,
                module_run_id=module_run_id,
                preprocessed=preprocessed,
            )
        return self._from_module_output(
            data,
            workflow_run_id=workflow_run_id,
            synthesis_id=synthesis_id,
            module_run_id=module_run_id,
            preprocessed=preprocessed,
        )

    def build_from_module_outputs(
        self,
        *,
        workflow_run_id: str,
        synthesis_id: str,
        preprocessed: SynthesisPreprocessResult,
        module_runs: list,
    ) -> SynthesisReport:
        high: list[Finding] = []
        moderate: list[Finding] = []
        exploratory: list[Finding] = []
        interventions: list[str] = []
        limitations: list[str] = []
        integrated_model: list[str] = []
        finding_index = 1

        for module_run in module_runs:
            if module_run.module_id == META_SYNTHESIS_MODULE_ID:
                continue
            if not module_run.parsed_output:
                continue

            output = module_run.parsed_output
            interventions.extend(output.get("recommendations", []))
            limitations.extend(output.get("limitations", []))

            for raw_finding in output.get("findings", []):
                finding = _normalize_finding(
                    raw_finding,
                    module_run_id=module_run.id,
                    index=finding_index,
                )
                finding_index += 1
                confidence = finding.confidence
                if confidence in _HIGH_CONFIDENCE:
                    high.append(finding)
                elif confidence in _MODERATE_CONFIDENCE:
                    moderate.append(finding)
                else:
                    exploratory.append(finding)

        summaries = [
            f"{module_id}: {summary}"
            for module_id, summary in preprocessed.module_summaries.items()
            if summary
        ]
        executive_summary = (
            "Integrated review across module outputs. "
            + " ".join(summaries[:3])
        ).strip()

        if preprocessed.convergence:
            integrated_model.append(
                "Shared evidence appears across modules in: "
                + "; ".join(preprocessed.convergence[:2])
            )

        return SynthesisReport(
            id=synthesis_id,
            workflow_run_id=workflow_run_id,
            executive_summary=executive_summary,
            high_confidence_findings=high,
            moderate_confidence_findings=moderate,
            exploratory_hypotheses=exploratory,
            convergence=preprocessed.convergence,
            divergence=preprocessed.divergence,
            integrated_model=integrated_model,
            interventions=_dedupe(interventions),
            outstanding_questions=[],
            limitations=_dedupe(limitations),
            source_module_run_ids=preprocessed.source_module_run_ids,
        )

    def _from_synthesis_output(
        self,
        data: dict[str, Any],
        *,
        workflow_run_id: str,
        synthesis_id: str,
        module_run_id: str,
        preprocessed: SynthesisPreprocessResult,
    ) -> SynthesisReport:
        try:
            parsed = SynthesisOutputInput.model_validate(data)
        except ValidationError as exc:
            raise OutputParseError(f"Invalid synthesis output shape: {exc}") from exc

        return SynthesisReport(
            id=synthesis_id,
            workflow_run_id=workflow_run_id,
            executive_summary=parsed.executive_summary.strip(),
            high_confidence_findings=[
                _normalize_finding_input(item, module_run_id, index)
                for index, item in enumerate(parsed.high_confidence_findings, start=1)
            ],
            moderate_confidence_findings=[
                _normalize_finding_input(item, module_run_id, index)
                for index, item in enumerate(
                    parsed.moderate_confidence_findings, start=1
                )
            ],
            exploratory_hypotheses=[
                _normalize_finding_input(item, module_run_id, index)
                for index, item in enumerate(parsed.exploratory_hypotheses, start=1)
            ],
            convergence=_merge_lists(parsed.convergence, preprocessed.convergence),
            divergence=_merge_lists(parsed.divergence, preprocessed.divergence),
            integrated_model=list(parsed.integrated_model),
            interventions=list(parsed.interventions),
            outstanding_questions=list(parsed.outstanding_questions),
            limitations=list(parsed.limitations),
            source_module_run_ids=preprocessed.source_module_run_ids + [module_run_id],
        )

    def _from_module_output(
        self,
        data: dict[str, Any],
        *,
        workflow_run_id: str,
        synthesis_id: str,
        module_run_id: str,
        preprocessed: SynthesisPreprocessResult,
    ) -> SynthesisReport:
        findings = data.get("findings", [])
        high: list[Finding] = []
        moderate: list[Finding] = []
        exploratory: list[Finding] = []

        for index, raw_finding in enumerate(findings, start=1):
            finding = _normalize_finding(
                raw_finding,
                module_run_id=module_run_id,
                index=index,
            )
            if finding.confidence in _HIGH_CONFIDENCE:
                high.append(finding)
            elif finding.confidence in _MODERATE_CONFIDENCE:
                moderate.append(finding)
            else:
                exploratory.append(finding)

        return SynthesisReport(
            id=synthesis_id,
            workflow_run_id=workflow_run_id,
            executive_summary=str(data.get("executive_summary", "")).strip(),
            high_confidence_findings=high,
            moderate_confidence_findings=moderate,
            exploratory_hypotheses=exploratory,
            convergence=preprocessed.convergence,
            divergence=preprocessed.divergence,
            integrated_model=[],
            interventions=list(data.get("recommendations", [])),
            outstanding_questions=[],
            limitations=list(data.get("limitations", [])),
            source_module_run_ids=preprocessed.source_module_run_ids + [module_run_id],
        )


def _is_synthesis_output_shape(data: dict[str, Any]) -> bool:
    return any(
        key in data
        for key in (
            "high_confidence_findings",
            "moderate_confidence_findings",
            "exploratory_hypotheses",
            "convergence",
            "divergence",
        )
    )


def _normalize_finding_input(
    finding: FindingInput,
    module_run_id: str,
    index: int,
) -> Finding:
    return Finding(
        id=finding.id or f"SF{index:03d}",
        module_run_id=module_run_id,
        type=_coerce_enum(FindingType, finding.type, "finding type"),
        title=finding.title.strip(),
        summary=finding.summary.strip(),
        confidence=_coerce_enum(Confidence, finding.confidence, "confidence"),
        evidence_quote_ids=list(finding.evidence_quote_ids),
        alternative_explanations=list(finding.alternative_explanations),
        limitations=list(finding.limitations),
        construct_ids=list(finding.construct_ids),
    )


def _normalize_finding(
    raw_finding: dict[str, Any],
    *,
    module_run_id: str,
    index: int,
) -> Finding:
    return Finding(
        id=str(raw_finding.get("id") or f"SF{index:03d}"),
        module_run_id=module_run_id,
        type=_coerce_enum(FindingType, raw_finding.get("type", "observation"), "finding type"),
        title=str(raw_finding.get("title", "")).strip(),
        summary=str(raw_finding.get("summary", "")).strip(),
        confidence=_coerce_enum(
            Confidence,
            raw_finding.get("confidence", "moderate"),
            "confidence",
        ),
        evidence_quote_ids=list(raw_finding.get("evidence_quote_ids", [])),
        alternative_explanations=list(raw_finding.get("alternative_explanations", [])),
        limitations=list(raw_finding.get("limitations", [])),
        construct_ids=list(raw_finding.get("construct_ids", [])),
    )


def _merge_lists(primary: list[str], secondary: list[str]) -> list[str]:
    return _dedupe([*primary, *secondary])


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def new_synthesis_id() -> str:
    return str(uuid.uuid4())


synthesis_parser = SynthesisParser()
