"""Interactive exploration over stored workflow findings."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from backend.core.exceptions import ExplorationError, FindingNotFoundError, LLMError
from backend.db.base import get_session
from backend.domain.enums import WorkflowRunStatus
from backend.domain.finding import ModuleRun
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.workflow_run_repository import WorkflowRunRepository
from backend.services.llm_factory import get_llm_provider
from backend.services.llm_provider import LLMProvider
from backend.services.synthesis_engine import SynthesisEngine, synthesis_engine
from backend.services.transcript_service import TranscriptService, transcript_service
from backend.services.workflow_engine import WorkflowEngine, workflow_engine
from config.settings import settings

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "with",
}


@dataclass(frozen=True)
class IndexedFinding:
    key: str
    module_id: str
    module_run_id: str
    finding: dict


class ExplorationService:
    def __init__(
        self,
        workflows: WorkflowEngine | None = None,
        transcripts: TranscriptService | None = None,
        synthesis: SynthesisEngine | None = None,
        llm: LLMProvider | None = None,
        workflow_runs: WorkflowRunRepository | None = None,
        findings: FindingRepository | None = None,
        constructs: ConstructRepository | None = None,
    ) -> None:
        self._workflows = workflows or workflow_engine
        self._transcripts = transcripts or transcript_service
        self._synthesis = synthesis or synthesis_engine
        self._llm = llm or get_llm_provider()
        self._workflow_runs = workflow_runs or WorkflowRunRepository()
        self._findings = findings or FindingRepository()
        self._constructs = constructs or ConstructRepository()

    def list_findings(self, workflow_run_id: str) -> list[dict]:
        with get_session() as session:
            persisted = self._findings.list_by_workflow_run_id(session, workflow_run_id)
        if persisted:
            return [
                {
                    "finding_key": item["finding_key"],
                    "module_id": item["module_id"],
                    "module_run_id": item["module_run_id"],
                    "id": item["id"],
                    "type": item["type"],
                    "title": item["title"],
                    "summary": item["summary"],
                    "confidence": item["confidence"],
                    "evidence_quote_ids": item["evidence_quote_ids"],
                }
                for item in persisted
            ]
        _, module_runs = self._workflows.get_with_module_runs(workflow_run_id)
        return [_indexed_to_dict(item) for item in _index_findings(module_runs)]

    def get_finding_drilldown(self, workflow_run_id: str, finding_key: str) -> dict:
        workflow_run, module_runs = self._workflows.get_with_module_runs(workflow_run_id)
        indexed = _index_findings(module_runs)
        target = _find_indexed(indexed, finding_key)
        if target is None:
            raise FindingNotFoundError(f"Finding not found: {finding_key}")

        bundle = self._transcripts.get(workflow_run.transcript_id)
        quotes_by_id = {quote.quote_id: quote for quote in bundle.evidence_quotes}
        quote_ids = target.finding.get("evidence_quote_ids", [])
        evidence_chain = [
            _quote_to_dict(quotes_by_id[quote_id], bundle.speakers)
            for quote_id in quote_ids
            if quote_id in quotes_by_id
        ]
        related = _related_findings(target, indexed, quote_ids)
        constructs = _linked_constructs(target, module_runs)

        return {
            "finding_key": target.key,
            "finding": target.finding,
            "module_id": target.module_id,
            "module_run_id": target.module_run_id,
            "workflow_run_id": workflow_run_id,
            "transcript_id": workflow_run.transcript_id,
            "evidence_chain": evidence_chain,
            "related_findings": related,
            "linked_constructs": constructs,
        }

    def get_cross_module_alignment(self, workflow_run_id: str) -> dict:
        _, module_runs = self._workflows.get_with_module_runs(workflow_run_id)
        indexed = _index_findings(module_runs)
        agreements = _agreement_groups(indexed)
        disagreements = _disagreement_groups(indexed)

        synthesis_summary = None
        try:
            report = self._synthesis.get_report(workflow_run_id)
            synthesis_summary = {
                "convergence": report.convergence,
                "divergence": report.divergence,
                "outstanding_questions": report.outstanding_questions,
            }
        except Exception:
            synthesis_summary = None

        return {
            "workflow_run_id": workflow_run_id,
            "agreements": agreements,
            "disagreements": disagreements,
            "synthesis": synthesis_summary,
        }

    def get_knowledge_graph(self, workflow_run_id: str) -> dict:
        with get_session() as session:
            constructs = self._constructs.list_by_workflow_run_id(
                session, workflow_run_id, canonical_only=True
            )
        if constructs:
            nodes: dict[str, dict] = {}
            for construct in constructs:
                node_id = f"{construct['module_id']}:{construct['source_id']}"
                nodes[node_id] = {
                    "id": node_id,
                    "type": construct["ontology_type"],
                    "label": construct["label"],
                    "module_id": construct["module_id"],
                    "confidence": construct["confidence"],
                    "evidence_quote_ids": construct["evidence_quote_ids"],
                    "row_id": construct["row_id"],
                    "convergence_score": construct.get("convergence_score"),
                }
            return {
                "workflow_run_id": workflow_run_id,
                "nodes": list(nodes.values()),
                "edges": [],  # P3 fills from normalized relationships
                "source": "normalized",
            }

        _, module_runs = self._workflows.get_with_module_runs(workflow_run_id)
        nodes: dict[str, dict] = {}
        edges: list[dict] = []

        for module_run in module_runs:
            parsed = module_run.parsed_output or {}
            module_id = parsed.get("module_id") or module_run.module_id
            for construct in parsed.get("constructs", []):
                node_id = f"{module_id}:{construct.get('id', construct.get('label', 'construct'))}"
                nodes[node_id] = {
                    "id": node_id,
                    "type": construct.get("type", "construct"),
                    "label": construct.get("label", node_id),
                    "module_id": module_id,
                    "confidence": construct.get("confidence"),
                    "evidence_quote_ids": construct.get("evidence_quote_ids", []),
                }
            for relationship in parsed.get("relationships", []):
                source = relationship.get("source_construct_id")
                target = relationship.get("target_construct_id")
                if not source or not target:
                    continue
                edges.append(
                    {
                        "source": f"{module_id}:{source}",
                        "target": f"{module_id}:{target}",
                        "relationship_type": relationship.get("relationship_type", "related"),
                        "module_id": module_id,
                        "confidence": relationship.get("confidence"),
                    }
                )

        return {
            "workflow_run_id": workflow_run_id,
            "nodes": list(nodes.values()),
            "edges": edges,
            "source": "parsed_output",
        }

    def compare_workflow_runs(self, workflow_run_ids: list[str]) -> dict:
        if len(workflow_run_ids) < 2:
            raise ExplorationError("Provide at least two workflow run IDs to compare")

        runs: list[dict] = []
        for run_id in workflow_run_ids:
            workflow_run, module_runs = self._workflows.get_with_module_runs(run_id)
            if workflow_run.status != WorkflowRunStatus.COMPLETED.value:
                raise ExplorationError(f"Workflow run {run_id} is not completed")
            indexed = _index_findings(module_runs)
            runs.append(
                {
                    "workflow_run_id": run_id,
                    "workflow_id": workflow_run.workflow_id,
                    "transcript_id": workflow_run.transcript_id,
                    "completed_at": workflow_run.completed_at.isoformat()
                    if workflow_run.completed_at
                    else None,
                    "finding_count": len(indexed),
                    "findings": [_indexed_to_dict(item) for item in indexed],
                }
            )

        shared_themes = _shared_themes(runs)
        recurring_quotes = _recurring_quote_ids(runs)

        return {
            "workflow_run_ids": workflow_run_ids,
            "runs": runs,
            "shared_themes": shared_themes,
            "recurring_evidence_quote_ids": recurring_quotes,
        }

    def ask_followup(
        self,
        workflow_run_id: str,
        question: str,
        *,
        model: str | None = None,
        finding_key: str | None = None,
    ) -> dict:
        question = question.strip()
        if not question:
            raise ExplorationError("Question is required")

        workflow_run, module_runs = self._workflows.get_with_module_runs(workflow_run_id)
        if workflow_run.status != WorkflowRunStatus.COMPLETED.value:
            raise ExplorationError(
                f"Follow-up questions require a completed workflow run (status: {workflow_run.status})"
            )

        context = self._build_followup_context(
            workflow_run_id=workflow_run_id,
            module_runs=module_runs,
            transcript_id=workflow_run.transcript_id,
            finding_key=finding_key,
        )
        resolved_model = model or workflow_run.model_used or settings.default_llm_model
        if not resolved_model:
            raise ExplorationError(
                "No LLM model specified. Pass model in the request or configure "
                "DEFAULT_OLLAMA_MODEL / BEDROCK_MODEL_ID."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You help users explore stored relationship-analysis findings. "
                    "Answer only using the provided context. Cite evidence quote IDs "
                    "when relevant. If the context is insufficient, say what evidence "
                    "would help rather than inventing conclusions."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{json.dumps(context, ensure_ascii=True, indent=2)}\n\n"
                    f"Question: {question}"
                ),
            },
        ]
        try:
            answer = self._llm.chat(resolved_model, messages)
        except LLMError as exc:
            raise ExplorationError(f"LLM chat failed: {exc.message}") from exc
        return {
            "workflow_run_id": workflow_run_id,
            "finding_key": finding_key,
            "question": question,
            "answer": answer,
            "model_used": resolved_model,
            "context_scope": context.get("scope"),
        }

    def list_transcript_workflow_runs(self, transcript_id: str) -> list[dict]:
        self._transcripts.get(transcript_id)
        with get_session() as session:
            runs = self._workflow_runs.list_by_transcript_id(
                session,
                transcript_id,
                status=WorkflowRunStatus.COMPLETED.value,
            )
        return [
            {
                "id": run.id,
                "workflow_id": run.workflow_id,
                "transcript_id": run.transcript_id,
                "status": run.status,
                "model_used": run.model_used,
                "started_at": run.started_at.isoformat(),
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in runs
        ]

    def _build_followup_context(
        self,
        *,
        workflow_run_id: str,
        module_runs: list[ModuleRun],
        transcript_id: str,
        finding_key: str | None,
    ) -> dict:
        indexed = _index_findings(module_runs)
        bundle = self._transcripts.get(transcript_id)
        quotes_by_id = {quote.quote_id: quote for quote in bundle.evidence_quotes}

        if finding_key:
            target = _find_indexed(indexed, finding_key)
            if target is None:
                raise FindingNotFoundError(f"Finding not found: {finding_key}")
            scoped_findings = [target]
            scope = f"finding:{finding_key}"
        else:
            scoped_findings = indexed
            scope = "workflow_run"

        findings_payload = []
        quote_ids: set[str] = set()
        for item in scoped_findings:
            finding = item.finding
            quote_ids.update(finding.get("evidence_quote_ids", []))
            findings_payload.append(
                {
                    "finding_key": item.key,
                    "module_id": item.module_id,
                    "title": finding.get("title"),
                    "summary": finding.get("summary"),
                    "confidence": finding.get("confidence"),
                    "evidence_quote_ids": finding.get("evidence_quote_ids", []),
                    "alternative_explanations": finding.get("alternative_explanations", []),
                    "limitations": finding.get("limitations", []),
                }
            )

        evidence = [
            {
                "quote_id": quote_id,
                "text": quotes_by_id[quote_id].text,
                "speaker_id": quotes_by_id[quote_id].speaker_id,
            }
            for quote_id in sorted(quote_ids)
            if quote_id in quotes_by_id
        ]

        synthesis_payload = None
        try:
            report = self._synthesis.get_report(workflow_run_id)
            synthesis_payload = {
                "executive_summary": report.executive_summary,
                "convergence": report.convergence,
                "divergence": report.divergence,
                "outstanding_questions": report.outstanding_questions,
            }
        except Exception:
            synthesis_payload = None

        return {
            "scope": scope,
            "findings": findings_payload,
            "evidence_quotes": evidence,
            "synthesis": synthesis_payload,
        }


def _index_findings(module_runs: list[ModuleRun]) -> list[IndexedFinding]:
    indexed: list[IndexedFinding] = []
    for module_run in module_runs:
        if module_run.status != "completed" or not module_run.parsed_output:
            continue
        parsed = module_run.parsed_output
        module_id = parsed.get("module_id") or module_run.module_id
        for finding in parsed.get("findings", []):
            finding_id = finding.get("id") or finding.get("title", "finding")
            key = f"{module_id}:{finding_id}"
            indexed.append(
                IndexedFinding(
                    key=key,
                    module_id=module_id,
                    module_run_id=module_run.id,
                    finding=finding,
                )
            )
    return indexed


def _indexed_to_dict(item: IndexedFinding) -> dict:
    return {
        "finding_key": item.key,
        "module_id": item.module_id,
        "module_run_id": item.module_run_id,
        "id": item.finding.get("id"),
        "type": item.finding.get("type"),
        "title": item.finding.get("title"),
        "summary": item.finding.get("summary"),
        "confidence": item.finding.get("confidence"),
        "evidence_quote_ids": item.finding.get("evidence_quote_ids", []),
    }


def _find_indexed(indexed: list[IndexedFinding], finding_key: str) -> IndexedFinding | None:
    for item in indexed:
        if item.key == finding_key:
            return item
    return None


def _quote_to_dict(quote, speakers) -> dict:
    speaker_name = next(
        (speaker.display_name or speaker.label for speaker in speakers if speaker.id == quote.speaker_id),
        "Speaker",
    )
    return {
        "quote_id": quote.quote_id,
        "text": quote.text,
        "speaker": speaker_name,
        "turn_index": quote.quote_index,
        "context_before": quote.context_before,
        "context_after": quote.context_after,
    }


def _related_findings(
    target: IndexedFinding,
    indexed: list[IndexedFinding],
    quote_ids: list[str],
) -> list[dict]:
    quote_set = set(quote_ids)
    related: list[dict] = []
    for item in indexed:
        if item.key == target.key:
            continue
        overlap = quote_set.intersection(item.finding.get("evidence_quote_ids", []))
        if not overlap:
            continue
        related.append(
            {
                "finding_key": item.key,
                "module_id": item.module_id,
                "title": item.finding.get("title"),
                "shared_evidence_quote_ids": sorted(overlap),
            }
        )
    return related


def _linked_constructs(target: IndexedFinding, module_runs: list[ModuleRun]) -> list[dict]:
    construct_ids = set(target.finding.get("construct_ids", []))
    if not construct_ids:
        return []

    linked: list[dict] = []
    for module_run in module_runs:
        if module_run.id != target.module_run_id:
            continue
        parsed = module_run.parsed_output or {}
        for construct in parsed.get("constructs", []):
            if construct.get("id") in construct_ids:
                linked.append(construct)
    return linked


def _tokenize_title(title: str) -> set[str]:
    tokens = {token for token in re.findall(r"[a-z0-9]+", title.lower()) if token not in _STOPWORDS}
    return tokens


def _agreement_groups(indexed: list[IndexedFinding]) -> list[dict]:
    groups: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    for left_index, left in enumerate(indexed):
        for right in indexed[left_index + 1 :]:
            pair_key = tuple(sorted((left.key, right.key)))
            if pair_key in seen_pairs:
                continue

            shared_quotes = set(left.finding.get("evidence_quote_ids", [])).intersection(
                right.finding.get("evidence_quote_ids", [])
            )
            title_overlap = _tokenize_title(left.finding.get("title", "")).intersection(
                _tokenize_title(right.finding.get("title", ""))
            )
            if not shared_quotes and len(title_overlap) < 2:
                continue

            seen_pairs.add(pair_key)
            groups.append(
                {
                    "finding_keys": [left.key, right.key],
                    "modules": [left.module_id, right.module_id],
                    "shared_evidence_quote_ids": sorted(shared_quotes),
                    "shared_title_terms": sorted(title_overlap),
                    "alignment": "agreement",
                }
            )
    return groups


def _disagreement_groups(indexed: list[IndexedFinding]) -> list[dict]:
    groups: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    for left_index, left in enumerate(indexed):
        for right in indexed[left_index + 1 :]:
            if left.module_id == right.module_id:
                continue
            pair_key = tuple(sorted((left.key, right.key)))
            if pair_key in seen_pairs:
                continue

            shared_quotes = set(left.finding.get("evidence_quote_ids", [])).intersection(
                right.finding.get("evidence_quote_ids", [])
            )
            if not shared_quotes:
                continue

            left_type = left.finding.get("type", "")
            right_type = right.finding.get("type", "")
            left_conf = left.finding.get("confidence", "")
            right_conf = right.finding.get("confidence", "")
            conflicting = left_type != right_type or (
                left_conf in {"low", "exploratory"} and right_conf in {"observed", "high"}
            )
            if not conflicting:
                continue

            seen_pairs.add(pair_key)
            groups.append(
                {
                    "finding_keys": [left.key, right.key],
                    "modules": [left.module_id, right.module_id],
                    "shared_evidence_quote_ids": sorted(shared_quotes),
                    "alignment": "tension",
                    "notes": [
                        f"{left.module_id} emphasizes {left_type or 'a different lens'}",
                        f"{right.module_id} emphasizes {right_type or 'a different lens'}",
                    ],
                }
            )
    return groups


def _shared_themes(runs: list[dict]) -> list[dict]:
    theme_map: dict[str, dict] = {}
    for run in runs:
        for finding in run["findings"]:
            for token in _tokenize_title(finding.get("title", "")):
                entry = theme_map.setdefault(
                    token,
                    {"theme": token, "workflow_run_ids": set(), "finding_keys": set()},
                )
                entry["workflow_run_ids"].add(run["workflow_run_id"])
                entry["finding_keys"].add(finding["finding_key"])

    shared = [
        {
            "theme": entry["theme"],
            "workflow_run_ids": sorted(entry["workflow_run_ids"]),
            "finding_keys": sorted(entry["finding_keys"]),
        }
        for entry in theme_map.values()
        if len(entry["workflow_run_ids"]) > 1
    ]
    return sorted(shared, key=lambda item: (-len(item["workflow_run_ids"]), item["theme"]))


def _recurring_quote_ids(runs: list[dict]) -> list[dict]:
    quote_map: dict[str, set[str]] = {}
    for run in runs:
        for finding in run["findings"]:
            for quote_id in finding.get("evidence_quote_ids", []):
                quote_map.setdefault(quote_id, set()).add(run["workflow_run_id"])

    return [
        {"quote_id": quote_id, "workflow_run_ids": sorted(run_ids)}
        for quote_id, run_ids in sorted(quote_map.items())
        if len(run_ids) > 1
    ]


exploration_service = ExplorationService()
