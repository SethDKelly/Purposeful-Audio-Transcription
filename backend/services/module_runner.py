"""Run analysis modules with compile, LLM call, parse, validate, and retry."""

import json
import logging
from typing import Any

from config.settings import settings
from backend.core.exceptions import ModuleRunError, OllamaError
from backend.core.module_registry import AnalysisModule, module_registry
from backend.core.purpose_registry import purpose_registry
from backend.db.base import get_session
from backend.domain.enums import TRANSCRIPT_RUNNABLE_MODULES, ModuleRunStatus
from backend.domain.finding import ModuleRun
from backend.repositories.module_run_repository import ModuleRunRepository, utc_now
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.module_output_validator import ModuleOutputValidator, module_output_validator
from backend.services.ollama_service import OllamaService, ollama_service
from backend.services.output_parser import OutputParseError, OutputParser, output_parser
from backend.services.prompt_compiler import CompiledPrompt
from backend.services.safety_validator import SafetyValidator, safety_validator
from backend.services.transcript_service import TranscriptService, transcript_service

logger = logging.getLogger(__name__)

_REPAIR_PROMPT = (
    "Your previous response failed validation. Return only a corrected JSON object "
    "matching module_output_v1. Fix these issues:\n\n{issues}\n\n"
    "Use only the provided evidence quote IDs. Include alternative_explanations "
    "for inferred findings. Do not exceed the module confidence ceiling."
)


class ModuleRunner:
    def __init__(
        self,
        registry=module_registry,
        purposes=purpose_registry,
        transcripts: TranscriptService | None = None,
        parser: OutputParser | None = None,
        validator: ModuleOutputValidator | None = None,
        safety: SafetyValidator | None = None,
        llm: OllamaService | None = None,
        repository: ModuleRunRepository | None = None,
    ) -> None:
        self._registry = registry
        self._purposes = purposes
        self._transcripts = transcripts or transcript_service
        self._parser = parser or output_parser
        self._validator = validator or module_output_validator
        self._safety = safety or safety_validator
        self._llm = llm or ollama_service
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
        compiled = self._purposes.build_compiled_messages(module_id, bundle)
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
        compiled = self._purposes.build_compiled_synthesis_messages(module_id, outputs_text)
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

        messages = list(compiled.messages)
        validation_errors: list[str] = []
        max_attempts = settings.module_run_max_retries + 1

        for attempt in range(max_attempts):
            status = ModuleRunStatus.RETRYING if attempt > 0 else ModuleRunStatus.RUNNING
            self._update_status(run, status)

            try:
                raw_output = self._llm.chat(resolved_model, messages)
            except OllamaError as exc:
                return self._fail_run(run, f"Ollama chat failed: {exc.message}")

            run.raw_output = raw_output
            self._persist_run(run)

            try:
                parsed_output = self._parse_and_validate(
                    raw_output,
                    module,
                    run.id,
                    valid_quote_ids,
                    require_evidence=require_evidence,
                )
            except OutputParseError as exc:
                validation_errors = [str(exc)]
            else:
                safety_result = self._safety.validate(parsed_output)
                if safety_result.violations:
                    validation_errors = safety_result.violations
                else:
                    return self._complete_run(
                        run,
                        parsed_output,
                        safety_result.flags,
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
        )

    def _ensure_transcript_runnable(self, module: AnalysisModule) -> None:
        if module.config.id not in TRANSCRIPT_RUNNABLE_MODULES:
            if module.config.input_type == "module_outputs":
                raise ModuleRunError(
                    f"Module {module.config.id} requires prior module outputs; "
                    "use the synthesis workflow instead."
                )
            raise ModuleRunError(f"Module {module.config.id} is not enabled for direct runs")

    def _resolve_model(self, module: AnalysisModule, model: str | None) -> str:
        resolved = model or module.config.ollama_model or settings.default_ollama_model or None
        if not resolved:
            raise ModuleRunError(
                "No Ollama model specified. Pass model in the request, set ollama_model "
                "in the module YAML, or set DEFAULT_OLLAMA_MODEL in .env."
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
    ) -> ModuleRunOutput:
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
        return output

    def _complete_run(
        self,
        run: ModuleRun,
        output: ModuleRunOutput,
        safety_flags: list[str],
    ) -> ModuleRun:
        run.status = ModuleRunStatus.COMPLETED.value
        run.parsed_output = output.model_dump(mode="json")
        run.validation_errors = None
        run.safety_flags = safety_flags or None
        run.completed_at = utc_now()
        self._persist_run(run)
        return run

    def _fail_run(
        self,
        run: ModuleRun,
        message: str,
        validation_errors: list[str] | None = None,
    ) -> ModuleRun:
        run.status = ModuleRunStatus.FAILED.value
        run.validation_errors = validation_errors or [message]
        run.completed_at = utc_now()
        self._persist_run(run)
        logger.warning("Module run %s failed: %s", run.id, message)
        return run

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
