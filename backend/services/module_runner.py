"""Run analysis modules with compile, LLM call, parse, validate, and retry."""

import json
import logging
import time
from collections.abc import Iterator
from typing import Any

from config.settings import settings
from backend.core.exceptions import LLMError, ModuleRunError
from backend.core.log_context import (
    log_context_extra,
    module_id_var,
    module_run_id_var,
    workflow_run_id_var,
)
from backend.core.module_registry import AnalysisModule, module_registry
from backend.services.prompt_compiler import PromptCompiler, prompt_compiler
from backend.db.base import get_session
from backend.domain.enums import ModuleRunStatus, SourceType
from backend.domain.finding import ModuleRun
from backend.domain.telemetry import ModuleRunTelemetry, estimate_cost_usd
from backend.repositories.module_run_repository import ModuleRunRepository, utc_now
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.module_output_validator import ModuleOutputValidator, module_output_validator
from backend.services.llm_factory import get_llm_provider
from backend.services.llm_provider import LLMProvider
from backend.services.output_parser import OutputParseError, OutputParser, output_parser
from backend.services.prompt_compiler import CompiledPrompt
from backend.services.safety_validator import SafetyValidator, safety_validator
from backend.services.transcript_service import TranscriptService, transcript_service

logger = logging.getLogger(__name__)

_REPAIR_PROMPT = (
    "Your previous response failed validation. Return only a corrected JSON object "
    "matching module_output_v1. Fix these issues:\n\n{issues}\n\n"
    "Use only the provided evidence quote IDs. Include alternative_explanations "
    "for inferred findings. Do not exceed the module confidence ceiling. "
    "Do not emit markdown outside the JSON object."
)


def compact_module_output_for_handoff(output: dict[str, Any]) -> dict[str, Any]:
    """Reduce token weight for meta-synthesis / prior-output handoffs.

    Keep structured fields Bedrock needs for convergence; drop duplicate prose
    already available to the UI via each module run's stored parsed_output.
    """
    compact = dict(output)
    compact["raw_markdown_report"] = ""
    return compact



class ModuleRunner:
    def __init__(
        self,
        registry=module_registry,
        compiler: PromptCompiler | None = None,
        transcripts: TranscriptService | None = None,
        parser: OutputParser | None = None,
        validator: ModuleOutputValidator | None = None,
        safety: SafetyValidator | None = None,
        llm: LLMProvider | None = None,
        repository: ModuleRunRepository | None = None,
    ) -> None:
        self._registry = registry
        self._compiler = compiler or prompt_compiler
        self._transcripts = transcripts or transcript_service
        self._parser = parser or output_parser
        self._validator = validator or module_output_validator
        self._safety = safety or safety_validator
        self._llm = llm or get_llm_provider()
        self._repository = repository or ModuleRunRepository()

    def run(
        self,
        module_id: str,
        transcript_id: str,
        model: str | None = None,
        workflow_run_id: str | None = None,
    ) -> ModuleRun:
        module = self._registry.get(module_id)
        self._ensure_transcript_runnable(module)

        bundle = self._transcripts.get(transcript_id)
        resolved_model = self._resolve_model(module, model)
        compiled = self._compiler.compile_for_transcript(module, bundle)
        valid_quote_ids = {quote.quote_id for quote in bundle.evidence_quotes}

        return self._execute(
            module=module,
            transcript_id=transcript_id,
            compiled=compiled,
            resolved_model=resolved_model,
            valid_quote_ids=valid_quote_ids,
            workflow_run_id=workflow_run_id,
            require_evidence=True,
        )

    def run_synthesis(
        self,
        module_id: str,
        transcript_id: str,
        prior_outputs: list[dict[str, Any]],
        model: str | None = None,
        workflow_run_id: str | None = None,
    ) -> ModuleRun:
        module = self._registry.get(module_id)
        if module.config.input_type != "module_outputs":
            raise ModuleRunError(f"Module {module_id} is not a synthesis module")

        bundle = self._transcripts.get(transcript_id)
        resolved_model = self._resolve_model(module, model)
        outputs_text = json.dumps(prior_outputs, indent=2)
        compiled = self._compiler.compile_for_module_outputs(module, outputs_text)
        valid_quote_ids = {quote.quote_id for quote in bundle.evidence_quotes}
        valid_quote_ids |= collect_quote_ids(prior_outputs)

        return self._execute(
            module=module,
            transcript_id=transcript_id,
            compiled=compiled,
            resolved_model=resolved_model,
            valid_quote_ids=valid_quote_ids,
            workflow_run_id=workflow_run_id,
            require_evidence=False,
        )

    def stream_for_transcript_text(
        self,
        module_id: str,
        transcript: str,
        model: str | None = None,
    ) -> Iterator[str]:
        module = self._registry.get(module_id)
        self._ensure_transcript_runnable(module)

        transcript = transcript.strip()
        if not transcript:
            raise ModuleRunError("Transcript is empty")

        bundle = self._transcripts.ingest(transcript, source_type=SourceType.PASTE)
        resolved_model = self._resolve_model(module, model)
        compiled = self._compiler.compile_for_transcript(module, bundle)
        try:
            yield from self._llm.chat_stream(resolved_model, compiled.messages)
        except LLMError as exc:
            raise ModuleRunError(f"LLM chat failed: {exc.message}") from exc

    def get(self, run_id: str) -> ModuleRun:
        with get_session() as session:
            return self._repository.get(session, run_id)

    def list_by_workflow_run(self, workflow_run_id: str) -> list[ModuleRun]:
        with get_session() as session:
            return self._repository.list_by_workflow_run_id(session, workflow_run_id)

    def _execute(
        self,
        *,
        module: AnalysisModule,
        transcript_id: str,
        compiled: CompiledPrompt,
        resolved_model: str,
        valid_quote_ids: set[str],
        workflow_run_id: str | None,
        require_evidence: bool,
    ) -> ModuleRun:
        workflow_token = workflow_run_id_var.set(workflow_run_id) if workflow_run_id else None
        module_token = module_id_var.set(module.config.id)
        try:
            with get_session() as session:
                run = self._repository.create(
                    session,
                    module_id=module.config.id,
                    transcript_id=transcript_id,
                    workflow_run_id=workflow_run_id,
                )
                run.status = ModuleRunStatus.RUNNING.value
                run.model_used = resolved_model
                run.module_version = compiled.module_version
                run.compiler_version = compiled.compiler_version
                run.prompt_template_hash = compiled.prompt_template_hash
                self._repository.save(session, run)

            run_id_token = module_run_id_var.set(run.id)
            try:
                messages = list(compiled.messages)
                validation_errors: list[str] = []
                max_attempts = settings.module_run_max_retries + 1
                total_latency_ms = 0
                total_input_tokens = 0
                total_output_tokens = 0
                total_cache_read = 0
                total_cache_write = 0
                validation_failure_count = 0

                for attempt in range(max_attempts):
                    status = ModuleRunStatus.RETRYING if attempt > 0 else ModuleRunStatus.RUNNING
                    self._update_status(run, status)

                    try:
                        chat_started = time.perf_counter()
                        if (
                            attempt == 0
                            and getattr(self._llm, "name", None) == "bedrock"
                            and hasattr(self._llm, "chat_cached")
                            and settings.bedrock_prompt_cache
                            and compiled.cache_user_prefix
                        ):
                            raw_output = self._llm.chat_cached(
                                resolved_model,
                                compiled,
                                json_mode=True,
                            )
                        else:
                            raw_output = self._llm.chat(
                                resolved_model, messages, json_mode=True
                            )
                        total_latency_ms += int((time.perf_counter() - chat_started) * 1000)
                        usage = getattr(self._llm, "last_usage", None) or {}
                        if isinstance(usage, dict):
                            total_input_tokens += int(usage.get("input_tokens") or 0)
                            total_output_tokens += int(usage.get("output_tokens") or 0)
                            total_cache_read += int(usage.get("cache_read_input_tokens") or 0)
                            total_cache_write += int(usage.get("cache_write_input_tokens") or 0)
                            if usage.get("latency_ms"):
                                # Prefer provider-measured latency when present.
                                total_latency_ms = max(
                                    total_latency_ms, int(usage["latency_ms"])
                                )
                    except LLMError as exc:
                        return self._fail_run(
                            run,
                            f"LLM chat failed: {exc.message}",
                            error_type="LLMError",
                            telemetry=self._build_telemetry(
                                model=resolved_model,
                                latency_ms=total_latency_ms,
                                retry_count=attempt,
                                input_tokens=total_input_tokens,
                                output_tokens=total_output_tokens,
                                cache_read=total_cache_read,
                                cache_write=total_cache_write,
                                validation_failure_count=validation_failure_count,
                            ),
                        )

                    run.raw_output = raw_output
                    self._persist_run(run)

                    try:
                        parsed_output, coverage_warnings, coverage = self._parse_and_validate(
                            raw_output,
                            module,
                            run.id,
                            valid_quote_ids,
                            require_evidence=require_evidence,
                        )
                    except OutputParseError as exc:
                        validation_errors = [str(exc)]
                        validation_failure_count += 1
                        logger.warning(
                            "Module output parse failed on attempt %s",
                            attempt + 1,
                            extra=log_context_extra(
                                event="module.run.parse_error",
                                error_type="OutputParseError",
                                module_run_id=run.id,
                                module_id=module.config.id,
                                workflow_run_id=workflow_run_id,
                                model_id=resolved_model,
                                retry_count=attempt,
                            ),
                        )
                    else:
                        safety_result = self._safety.validate(parsed_output)
                        if safety_result.violations:
                            validation_errors = safety_result.violations
                            validation_failure_count += 1
                        else:
                            telemetry = self._build_telemetry(
                                model=resolved_model,
                                latency_ms=total_latency_ms,
                                retry_count=attempt,
                                input_tokens=total_input_tokens,
                                output_tokens=total_output_tokens,
                                cache_read=total_cache_read,
                                cache_write=total_cache_write,
                                validation_failure_count=validation_failure_count,
                                output=parsed_output,
                                coverage=coverage,
                            )
                            return self._complete_run(
                                run,
                                parsed_output,
                                safety_result.flags,
                                validation_warnings=coverage_warnings,
                                construct_coverage=coverage,
                                telemetry=telemetry,
                            )

                    if attempt < max_attempts - 1:
                        messages = messages + [
                            {"role": "assistant", "content": raw_output},
                            {
                                "role": "user",
                                "content": _REPAIR_PROMPT.format(
                                    issues="\n".join(f"- {error}" for error in validation_errors)
                                ),
                            },
                        ]
                        continue

                return self._fail_run(
                    run,
                    "Module output failed validation after retries",
                    validation_errors=validation_errors,
                    error_type="ValidationError",
                    telemetry=self._build_telemetry(
                        model=resolved_model,
                        latency_ms=total_latency_ms,
                        retry_count=max_attempts - 1,
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        cache_read=total_cache_read,
                        cache_write=total_cache_write,
                        validation_failure_count=validation_failure_count,
                    ),
                )
            finally:
                module_run_id_var.reset(run_id_token)
        finally:
            module_id_var.reset(module_token)
            if workflow_token is not None:
                workflow_run_id_var.reset(workflow_token)

    def _ensure_transcript_runnable(self, module: AnalysisModule) -> None:
        if module.config.input_type == "transcript":
            return
        if module.config.input_type == "module_outputs":
            raise ModuleRunError(
                f"Module {module.config.id} requires prior module outputs; "
                "use the synthesis workflow instead."
            )
        raise ModuleRunError(f"Module {module.config.id} is not enabled for direct runs")

    def _resolve_model(self, module: AnalysisModule, model: str | None) -> str:
        resolved = (
            model
            or module.config.resolved_model_id
            or settings.default_llm_model
            or None
        )
        if not resolved:
            raise ModuleRunError(
                "No LLM model specified. Pass model in the request, set model_id in the "
                "module YAML, or configure BEDROCK_MODEL_ID."
            )
        return resolved

    def _parse_and_validate(
        self,
        raw_output: str,
        module: AnalysisModule,
        module_run_id: str,
        valid_quote_ids: set[str],
        *,
        require_evidence: bool = True,
    ) -> tuple[ModuleRunOutput, list[str], dict | None]:
        data = self._parser.extract_json(raw_output)
        output = self._parser.normalize(data, module, module_run_id)
        validation = self._validator.validate(
            output,
            module,
            valid_quote_ids,
            require_evidence=require_evidence,
        )
        if not validation.is_valid:
            raise OutputParseError("; ".join(validation.errors))
        coverage = (
            validation.construct_coverage.as_dict()
            if validation.construct_coverage is not None
            else None
        )
        return output, list(validation.warnings), coverage

    def _complete_run(
        self,
        run: ModuleRun,
        output: ModuleRunOutput,
        safety_flags: list[str],
        validation_warnings: list[str] | None = None,
        construct_coverage: dict | None = None,
        telemetry: dict | None = None,
    ) -> ModuleRun:
        # Cap stored markdown so UI/synthesis stay lean even if the model sprawls.
        markdown = (output.raw_markdown_report or "").strip()
        if len(markdown) > 1200:
            output.raw_markdown_report = markdown[:1200].rstrip() + "..."
        run.status = ModuleRunStatus.COMPLETED.value
        parsed = output.model_dump(mode="json")
        if construct_coverage is not None:
            parsed["construct_coverage"] = construct_coverage
        run.parsed_output = parsed
        run.validation_errors = None
        run.validation_warnings = validation_warnings or None
        run.safety_flags = safety_flags or None
        run.telemetry = telemetry
        run.completed_at = utc_now()
        self._persist_run(run)
        if telemetry:
            logger.info(
                "Module run %s telemetry",
                run.id,
                extra={
                    "event": "module.run.telemetry",
                    "module_id": run.module_id,
                    "telemetry": telemetry,
                },
            )
        return run

    def _fail_run(
        self,
        run: ModuleRun,
        message: str,
        validation_errors: list[str] | None = None,
        *,
        error_type: str = "ModuleRunFailed",
        telemetry: dict | None = None,
    ) -> ModuleRun:
        run.status = ModuleRunStatus.FAILED.value
        run.validation_errors = validation_errors or [message]
        run.telemetry = telemetry
        run.completed_at = utc_now()
        self._persist_run(run)
        logger.error(
            "Module run %s failed: %s",
            run.id,
            message,
            extra=log_context_extra(
                event="module.run.failed",
                error_type=error_type,
                module_run_id=run.id,
                module_id=run.module_id,
                workflow_run_id=run.workflow_run_id,
                model_id=run.model_used,
            ),
        )
        return run

    def _build_telemetry(
        self,
        *,
        model: str | None,
        latency_ms: int,
        retry_count: int,
        input_tokens: int,
        output_tokens: int,
        cache_read: int,
        cache_write: int,
        validation_failure_count: int,
        output: ModuleRunOutput | None = None,
        coverage: dict | None = None,
    ) -> dict:
        cost = estimate_cost_usd(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_input_tokens=cache_read,
            cache_write_input_tokens=cache_write,
            input_per_mtok=settings.bedrock_input_cost_per_mtok,
            output_per_mtok=settings.bedrock_output_cost_per_mtok,
            cache_read_per_mtok=settings.bedrock_cache_read_cost_per_mtok,
            cache_write_per_mtok=settings.bedrock_cache_write_cost_per_mtok,
        )
        quote_ids: set[str] = set()
        finding_count = 0
        construct_count = 0
        relationship_count = 0
        if output is not None:
            finding_count = len(output.findings)
            construct_count = len(output.constructs)
            relationship_count = len(output.relationships)
            for finding in output.findings:
                quote_ids.update(finding.evidence_quote_ids)
            for construct in output.constructs:
                quote_ids.update(construct.evidence_quote_ids)
        coverage_rate = None
        if coverage is not None:
            coverage_rate = coverage.get("coverage_rate")
        return ModuleRunTelemetry(
            model=model,
            latency_ms=latency_ms,
            retry_count=retry_count,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_input_tokens=cache_read,
            cache_write_input_tokens=cache_write,
            estimated_cost_usd=cost,
            finding_count=finding_count,
            construct_count=construct_count,
            relationship_count=relationship_count,
            evidence_quote_count=len(quote_ids),
            validation_failure_count=validation_failure_count,
            coverage_rate=coverage_rate,
        ).as_dict()

    def _update_status(self, run: ModuleRun, status: ModuleRunStatus) -> None:
        run.status = status.value
        self._persist_run(run)

    def _persist_run(self, run: ModuleRun) -> None:
        with get_session() as session:
            self._repository.save(session, run)


def collect_quote_ids(outputs: list[dict[str, Any]]) -> set[str]:
    quote_ids: set[str] = set()
    for output in outputs:
        for finding in output.get("findings", []):
            quote_ids.update(finding.get("evidence_quote_ids", []))
        for construct in output.get("constructs", []):
            quote_ids.update(construct.get("evidence_quote_ids", []))
    return quote_ids


module_runner = ModuleRunner()
