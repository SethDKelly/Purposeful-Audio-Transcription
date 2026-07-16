"""Compile module definitions and evidence into LLM messages."""

import hashlib
import re
from dataclasses import dataclass

from backend.core.module_registry import AnalysisModule
from backend.domain.enums import Confidence
from backend.domain.transcript import TranscriptBundle
from backend.services.evidence_index import EvidenceIndexService
from config.settings import settings

COMPILER_VERSION = "1.2.0"
_VERSION_PATTERN = re.compile(r"version:\s*([\d.]+)", re.IGNORECASE)


@dataclass(frozen=True)
class CompiledPrompt:
    messages: list[dict[str, str]]
    module_id: str
    module_version: str
    compiler_version: str
    shared_instructions_version: str
    output_schema_id: str
    prompt_template_hash: str
    confidence_ceiling: Confidence
    # Stable prefixes for Bedrock prompt caching (framework + evidence/priors).
    cache_system_text: str = ""
    cache_user_prefix: str = ""
    cache_user_suffix: str = ""


class PromptCompiler:
    def __init__(
        self,
        framework_dir=None,
        evidence_index: EvidenceIndexService | None = None,
    ) -> None:
        self._framework_dir = framework_dir or settings.framework_dir
        self._evidence_index = evidence_index or EvidenceIndexService()
        self._shared_instructions = self._load_framework_file("shared_instructions.md")
        self._output_schema_instructions = self._load_framework_file(
            "output_schema_instructions.md"
        )
        self._shared_instructions_version = _read_version(self._shared_instructions)

    def _load_framework_file(self, filename: str) -> str:
        path = self._framework_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Framework file not found: {path}")
        return path.read_text(encoding="utf-8").strip()

    def compile_for_transcript(
        self,
        module: AnalysisModule,
        bundle: TranscriptBundle,
    ) -> CompiledPrompt:
        if module.config.input_type != "transcript":
            raise ValueError(
                f"Module {module.config.id} expects input_type={module.config.input_type}"
            )

        evidence_text = self._evidence_index.format_for_prompt(
            bundle.evidence_quotes,
            bundle.speakers,
        )
        user_prefix = self._build_evidence_user_prefix(evidence_text)
        user_suffix = self._build_transcript_user_task(module)
        return self._compile(module, user_prefix=user_prefix, user_suffix=user_suffix)

    def compile_for_module_outputs(
        self,
        module: AnalysisModule,
        module_outputs: str,
        *,
        safety_mode: bool = False,
    ) -> CompiledPrompt:
        if module.config.input_type != "module_outputs":
            raise ValueError(
                f"Module {module.config.id} expects input_type={module.config.input_type}"
            )

        user_prefix = self._build_module_outputs_user_prefix(module_outputs)
        user_suffix = self._build_module_outputs_user_task(module, safety_mode=safety_mode)
        return self._compile(module, user_prefix=user_prefix, user_suffix=user_suffix)

    def _compile(
        self,
        module: AnalysisModule,
        *,
        user_prefix: str,
        user_suffix: str,
    ) -> CompiledPrompt:
        cache_system = self._build_cacheable_system()
        module_system = self._build_module_system(module)
        system_content = "\n\n---\n\n".join(
            section for section in (cache_system, module_system) if section
        )
        user_content = f"{user_prefix.strip()}\n\n{user_suffix.strip()}"
        prompt_template_hash = _hash_text(
            system_content,
            user_content,
            module.config.version,
            COMPILER_VERSION,
            self._shared_instructions_version,
        )
        return CompiledPrompt(
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            module_id=module.config.id,
            module_version=module.config.version,
            compiler_version=COMPILER_VERSION,
            shared_instructions_version=self._shared_instructions_version,
            output_schema_id=module.config.output_schema,
            prompt_template_hash=prompt_template_hash,
            confidence_ceiling=module.config.confidence_ceiling,
            cache_system_text=cache_system,
            cache_user_prefix=user_prefix,
            cache_user_suffix=f"{module_system}\n\n---\n\n{user_suffix}".strip(),
        )

    def _build_cacheable_system(self) -> str:
        sections = [self._shared_instructions, self._output_schema_instructions]
        return "\n\n---\n\n".join(section for section in sections if section)

    def _build_module_system(self, module: AnalysisModule) -> str:
        sections = [
            self._build_module_role_section(module),
            module.module_prompt,
            self._build_validation_section(module),
        ]
        return "\n\n---\n\n".join(section for section in sections if section)

    def _build_module_role_section(self, module: AnalysisModule) -> str:
        config = module.config
        secondary = ""
        if config.secondary_questions:
            questions = "\n".join(f"- {question}" for question in config.secondary_questions)
            secondary = f"\n\nSecondary questions:\n{questions}"

        constructs = ""
        if config.required_constructs:
            joined = ", ".join(config.required_constructs)
            constructs = f"\n\nRequired constructs to consider: {joined}"

        return (
            f"# Module Role\n\n"
            f"You are analyzing through a **{config.primary_lens}** lens.\n\n"
            f"Module: {config.name} (v{config.version})\n"
            f"Analytical level: {config.analytical_level.value}\n"
            f"Unit of analysis: {config.unit_of_analysis}\n"
            f"Inference depth: {config.inference_depth}\n"
            f"Confidence ceiling: {config.confidence_ceiling.value}\n\n"
            f"Primary question: {config.primary_question}"
            f"{secondary}"
            f"{constructs}"
        )

    def _build_validation_section(self, module: AnalysisModule) -> str:
        return (
            "# Validation Requirements\n\n"
            f"- Do not assign confidence above **{module.config.confidence_ceiling.value}**.\n"
            "- Every finding must cite at least one evidence quote ID unless it is a "
            "general methodological limitation.\n"
            "- Inferred findings must include at least one alternative explanation.\n"
            "- Use only quote IDs provided in the evidence index.\n"
            "- Prefer structured `findings` / `constructs` over long prose; keep "
            "`raw_markdown_report` empty or under ~150 words."
        )

    def _build_evidence_user_prefix(self, evidence_text: str) -> str:
        return (
            "## Evidence Index\n\n"
            "Each line is a quotable turn. Cite using the bracketed quote ID.\n\n"
            f"{evidence_text}"
        )

    def _build_transcript_user_task(self, module: AnalysisModule) -> str:
        return (
            f"Analyze the conversation using the **{module.config.name}** module.\n\n"
            "Return only one JSON object matching module_output_v1. "
            "Put primary analysis in structured fields. "
            "Leave `raw_markdown_report` empty unless a short prose note is essential."
        )

    def _build_module_outputs_user_prefix(self, module_outputs: str) -> str:
        return (
            "Do not re-analyze the raw transcript. Use only the structured outputs below.\n\n"
            "## Prior Module Outputs\n\n"
            f"{module_outputs.strip()}"
        )

    def _build_module_outputs_user_task(
        self, module: AnalysisModule, *, safety_mode: bool = False
    ) -> str:
        sections = [
            f"Synthesize the prior module outputs using the **{module.config.name}** module.\n\n"
            "Return only one JSON object matching module_output_v1. "
            "Prefer structured synthesis fields; keep `raw_markdown_report` brief or empty."
        ]
        if safety_mode:
            from backend.services.safety_risk_scanner import SAFETY_SYNTHESIS_FRAMING

            sections.append(SAFETY_SYNTHESIS_FRAMING)
        return "\n\n".join(sections)


def _read_version(text: str) -> str:
    match = _VERSION_PATTERN.search(text)
    return match.group(1) if match else "unknown"


def _hash_text(*parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


prompt_compiler = PromptCompiler()
