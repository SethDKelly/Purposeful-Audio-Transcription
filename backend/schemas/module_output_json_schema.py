"""JSON Schema for Bedrock structured outputs (module_output_v1)."""

from __future__ import annotations

from backend.domain.enums import Confidence, FindingType, RelationshipType

_FINDING_TYPES = sorted(item.value for item in FindingType)
_CONFIDENCES = sorted(item.value for item in Confidence)
_RELATIONSHIP_TYPES = sorted(item.value for item in RelationshipType)

MODULE_OUTPUT_V1_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "module_id",
        "module_version",
        "executive_summary",
        "findings",
        "constructs",
        "relationships",
        "recommendations",
        "limitations",
        "raw_markdown_report",
    ],
    "properties": {
        "module_id": {"type": "string"},
        "module_version": {"type": "string"},
        "executive_summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "type",
                    "title",
                    "summary",
                    "confidence",
                    "evidence_quote_ids",
                    "alternative_explanations",
                    "limitations",
                    "construct_ids",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "module_run_id": {"type": "string"},
                    "type": {"type": "string", "enum": _FINDING_TYPES},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "confidence": {"type": "string", "enum": _CONFIDENCES},
                    "evidence_quote_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "alternative_explanations": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "construct_ids": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "constructs": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "type",
                    "label",
                    "confidence",
                    "evidence_quote_ids",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "label": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "confidence": {"type": "string", "enum": _CONFIDENCES},
                    "evidence_quote_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "source_construct_id",
                    "target_construct_id",
                    "relationship_type",
                    "confidence",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "source_construct_id": {"type": "string"},
                    "target_construct_id": {"type": "string"},
                    "relationship_type": {
                        "type": "string",
                        "enum": _RELATIONSHIP_TYPES,
                    },
                    "confidence": {"type": "string", "enum": _CONFIDENCES},
                },
            },
        },
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "raw_markdown_report": {"type": "string"},
    },
}
