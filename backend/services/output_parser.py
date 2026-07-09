"""Extract and normalize structured JSON from LLM responses."""

import json
import re
from typing import Any

from pydantic import ValidationError

from backend.core.module_registry import AnalysisModule
from backend.domain.enums import Confidence, FindingType, RelationshipType
from backend.domain.finding import Construct, ConstructRelationship, Finding
from backend.schemas.module_output_v1 import (
    ConstructInput,
    ConstructRelationshipInput,
    FindingInput,
    ModuleRunOutput,
    ModuleRunOutputInput,
)

_JSON_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.DOTALL | re.IGNORECASE,
)


class OutputParseError(ValueError):
    pass


class OutputParser:
    def extract_json(self, raw_output: str) -> dict[str, Any]:
        raw_output = raw_output.strip()
        if not raw_output:
            raise OutputParseError("LLM returned empty output")

        fenced = _JSON_FENCE_PATTERN.search(raw_output)
        if fenced:
            return _loads_json(fenced.group(1))

        brace_match = _extract_balanced_object(raw_output)
        if brace_match:
            return _loads_json(brace_match)

        raise OutputParseError("No JSON object found in LLM output")

    def parse_input(self, data: dict[str, Any]) -> ModuleRunOutputInput:
        try:
            return ModuleRunOutputInput.model_validate(data)
        except ValidationError as exc:
            raise OutputParseError(f"Invalid module output shape: {exc}") from exc

    def normalize(
        self,
        data: dict[str, Any],
        module: AnalysisModule,
        module_run_id: str,
    ) -> ModuleRunOutput:
        parsed = self.parse_input(data)
        findings = [
            _normalize_finding(finding, module_run_id, index)
            for index, finding in enumerate(parsed.findings, start=1)
        ]
        constructs = [
            _normalize_construct(construct, index)
            for index, construct in enumerate(parsed.constructs, start=1)
        ]
        relationships = [
            _normalize_relationship(relationship, index)
            for index, relationship in enumerate(parsed.relationships, start=1)
        ]
        return ModuleRunOutput(
            module_id=module.config.id,
            module_version=module.config.version,
            executive_summary=parsed.executive_summary.strip(),
            findings=findings,
            constructs=constructs,
            relationships=relationships,
            recommendations=[item.strip() for item in parsed.recommendations if item.strip()],
            limitations=[item.strip() for item in parsed.limitations if item.strip()],
            raw_markdown_report=parsed.raw_markdown_report.strip(),
        )


def _loads_json(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OutputParseError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise OutputParseError("Module output JSON must be an object")
    return data


def _extract_balanced_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def _normalize_finding(
    finding: FindingInput,
    module_run_id: str,
    index: int,
) -> Finding:
    finding_type = _coerce_enum(FindingType, finding.type, "finding type")
    confidence = _coerce_enum(Confidence, finding.confidence, "confidence")
    return Finding(
        id=finding.id or f"F{index:03d}",
        module_run_id=module_run_id,
        type=finding_type,
        title=finding.title.strip(),
        summary=finding.summary.strip(),
        confidence=confidence,
        evidence_quote_ids=list(finding.evidence_quote_ids),
        alternative_explanations=[
            item.strip() for item in finding.alternative_explanations if item.strip()
        ],
        limitations=[item.strip() for item in finding.limitations if item.strip()],
        construct_ids=list(finding.construct_ids),
    )


def _normalize_construct(construct: ConstructInput, index: int) -> Construct:
    return Construct(
        id=construct.id or f"C{index:03d}",
        type=construct.type.strip(),
        label=construct.label.strip(),
        description=construct.description.strip() if construct.description else None,
        confidence=_coerce_enum(Confidence, construct.confidence, "construct confidence"),
        evidence_quote_ids=list(construct.evidence_quote_ids),
    )


def _normalize_relationship(
    relationship: ConstructRelationshipInput,
    index: int,
) -> ConstructRelationship:
    return ConstructRelationship(
        id=relationship.id or f"R{index:03d}",
        source_construct_id=relationship.source_construct_id,
        target_construct_id=relationship.target_construct_id,
        relationship_type=_coerce_enum(
            RelationshipType,
            relationship.relationship_type,
            "relationship type",
        ),
        confidence=_coerce_enum(Confidence, relationship.confidence, "relationship confidence"),
    )


def _coerce_enum(enum_cls, value, label: str):
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(str(value).strip().lower())
    except ValueError as exc:
        raise OutputParseError(f"Invalid {label}: {value}") from exc


output_parser = OutputParser()
