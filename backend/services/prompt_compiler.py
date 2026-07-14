"""Compile module definitions and evidence into LLM messages."""

import hashlib
import re
from dataclasses import dataclass

from backend.core.module_registry import AnalysisModule
from backend.domain.enums import Confidence
from backend.domain.transcript import TranscriptBundle
from backend.services.evidence_index import EvidenceIndexService
from config.settings import settings

COMPILER_VERSION = "1.1.0"
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
        user_content = self._build_transcript_user_message(module, evidence_text)
        return self._compile(module, user_content)

    def compile_for_module_outputs(
        self,
        module: AnalysisModule,
        module_outputs: str,
    ) -> CompiledPrompt:
        if module.config.input_type != "module_outputs":
            raise ValueError(
                f"Module {module.config.id} expects input_type={module.config.input_type}"
            )

        user_content = self._build_module_outputs_user_message(module, module_outputs)
        return self._compile(module, user_content)

    def _compile(self, module: AnalysisModule, user_content: str) -> CompiledPrompt:
        system_content = self._build_system_message(module)
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
        )

    def _build_system_message(self, module: AnalysisModule) -> str:
        sections = [
            self._shared_instructions,
            self._build_module_role_section(module),
            module.module_prompt,
            self._build_validation_section(module),
            self._output_schema_instructions,
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
            "- Use only quote IDs provided in the evidence index."
        )

    def _build_transcript_user_message(
        self,
        module: AnalysisModule,
        evidence_text: str,
    ) -> str:
        return (
            f"Analyze the conversation using the **{module.config.name}** module.\n\n"
            "## Evidence Index\n\n"
            "Each line is a quotable turn. Cite using the bracketed quote ID.\n\n"
            f"{evidence_text}\n\n"
            "Return only one JSON object matching module_output_v1. "
            "Put the human-readable report inside raw_markdown_report."
        )

    def _build_module_outputs_user_message(
        self,
        module: AnalysisModule,
        module_outputs: str,
    ) -> str:
        return (
            f"Synthesize the prior module outputs using the **{module.config.name}** module.\n\n"
            "Do not re-analyze the raw transcript. Use only the structured outputs below.\n\n"
            "## Prior Module Outputs\n\n"
            f"{module_outputs.strip()}\n\n"
            "Return only one JSON object matching module_output_v1. "
            "Put the human-readable report inside raw_markdown_report."
        )


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
