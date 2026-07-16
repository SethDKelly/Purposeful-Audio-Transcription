"""Extract and normalize structured JSON from LLM responses."""

import json
import logging
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

_JSON_FENCE_WRAPPER = re.compile(
    r"```(?:json)?\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)

logger = logging.getLogger(__name__)

# Bedrock often omits alternatives on inferred findings; fill so validation can pass.
_INFERRED_CONFIDENCES = {
    Confidence.HIGH,
    Confidence.MODERATE,
    Confidence.LOW,
    Confidence.EXPLORATORY,
}
_DEFAULT_ALTERNATIVE = (
    "Other readings of the same evidence remain plausible; "
    "this finding is inferred rather than directly observed."
)


class OutputParseError(ValueError):
    pass


class OutputParser:
    def extract_json(self, raw_output: str) -> dict[str, Any]:
        raw_output = raw_output.strip()
        if not raw_output:
            logger.warning(
                "Empty LLM output",
                extra={"event": "module.output.empty", "error_type": "OutputParseError"},
            )
            raise OutputParseError("LLM returned empty output")

        fenced = _JSON_FENCE_WRAPPER.search(raw_output)
        if fenced:
            candidate = fenced.group(1).strip()
            if candidate.startswith("{"):
                brace_match = _extract_balanced_object(candidate)
                if brace_match:
                    return _loads_json(brace_match)
                raise OutputParseError(
                    "JSON in code fence appears truncated or incomplete"
                )

        brace_match = _extract_balanced_object(raw_output)
        if brace_match:
            return _loads_json(brace_match)

        raise OutputParseError("No JSON object found in LLM output")

    def parse_input(self, data: dict[str, Any]) -> ModuleRunOutputInput:
        try:
            return ModuleRunOutputInput.model_validate(_coerce_raw_module_payload(data))
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


def _coerce_raw_module_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Fill common LLM field aliases/defaults before strict schema validation."""
    coerced = dict(data)

    constructs: list[dict[str, Any]] = []
    for index, raw in enumerate(coerced.get("constructs") or [], start=1):
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        construct_id = str(item.get("id") or f"C{index:03d}")
        item["id"] = construct_id
        if not item.get("type"):
            item["type"] = str(
                item.get("construct_type") or item.get("category") or construct_id
            )
        if not item.get("label"):
            item["label"] = str(
                item.get("name")
                or item.get("title")
                or construct_id.replace("_", " ")
            )
        if not item.get("description") and item.get("summary"):
            item["description"] = item.get("summary")
        if not item.get("confidence"):
            item["confidence"] = "exploratory"
        constructs.append(item)
    coerced["constructs"] = constructs

    relationships: list[dict[str, Any]] = []
    for index, raw in enumerate(coerced.get("relationships") or [], start=1):
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        if not item.get("id"):
            item["id"] = f"R{index:03d}"
        if not item.get("source_construct_id"):
            source = item.get("source_id") or item.get("source") or item.get("from")
            if source is not None:
                item["source_construct_id"] = str(source)
        if not item.get("target_construct_id"):
            target = item.get("target_id") or item.get("target") or item.get("to")
            if target is not None:
                item["target_construct_id"] = str(target)
        if not item.get("relationship_type"):
            item["relationship_type"] = str(
                item.get("type") or item.get("relation") or "co_occurs_with"
            )
        if not item.get("confidence"):
            item["confidence"] = "exploratory"
        if item.get("source_construct_id") and item.get("target_construct_id"):
            relationships.append(item)
    coerced["relationships"] = relationships
    return coerced


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
    alternatives = [
        item.strip() for item in finding.alternative_explanations if item.strip()
    ]
    if confidence in _INFERRED_CONFIDENCES and not alternatives:
        alternatives = [_DEFAULT_ALTERNATIVE]
    return Finding(
        id=finding.id or f"F{index:03d}",
        module_run_id=module_run_id,
        type=finding_type,
        title=finding.title.strip(),
        summary=finding.summary.strip(),
        confidence=confidence,
        evidence_quote_ids=list(finding.evidence_quote_ids),
        alternative_explanations=alternatives,
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
    text = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    try:
        return enum_cls(text)
    except ValueError:
        if enum_cls is RelationshipType:
            aliases = {
                "reinforce": RelationshipType.SUPPORTS,
                "reinforces": RelationshipType.SUPPORTS,
                "supports": RelationshipType.SUPPORTS,
                "leads_to": RelationshipType.CONTRIBUTES_TO,
                "causes": RelationshipType.CONTRIBUTES_TO,
                "triggers": RelationshipType.ESCALATES,
                "related_to": RelationshipType.CO_OCCURS_WITH,
                "related": RelationshipType.CO_OCCURS_WITH,
                "links": RelationshipType.CO_OCCURS_WITH,
            }
            if text in aliases:
                return aliases[text]
            logger.warning(
                "Unknown relationship type %r; defaulting to co_occurs_with",
                value,
            )
            return RelationshipType.CO_OCCURS_WITH
        raise OutputParseError(f"Invalid {label}: {value}") from None


output_parser = OutputParser()
