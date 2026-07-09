from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import Confidence, SourceType
from backend.services.prompt_compiler import COMPILER_VERSION, PromptCompiler
from backend.services.transcript_service import TranscriptService


def _sample_bundle():
    service = TranscriptService()
    return service.ingest(
        "Person A: I feel unheard when plans change.\nPerson B: I did not mean to dismiss you.",
        source_type=SourceType.PASTE,
    )


def test_prompt_compiler_is_deterministic() -> None:
    registry = ModuleRegistry()
    compiler = PromptCompiler()
    module = registry.get("relationship_conversation_analysis")
    bundle = _sample_bundle()

    first = compiler.compile_for_transcript(module, bundle)
    second = compiler.compile_for_transcript(module, bundle)

    assert first.prompt_template_hash == second.prompt_template_hash
    assert first.messages == second.messages


def test_prompt_compiler_includes_evidence_index() -> None:
    registry = ModuleRegistry()
    compiler = PromptCompiler()
    module = registry.get("systems_analysis")
    bundle = _sample_bundle()

    compiled = compiler.compile_for_transcript(module, bundle)
    user_message = compiled.messages[1]["content"]

    assert "[Q001]" in user_message
    assert "[Q002]" in user_message
    assert "Evidence Index" in user_message


def test_prompt_compiler_includes_shared_rules_and_schema() -> None:
    registry = ModuleRegistry()
    compiler = PromptCompiler()
    module = registry.get("nvc_analysis")
    bundle = _sample_bundle()

    compiled = compiler.compile_for_transcript(module, bundle)
    system_message = compiled.messages[0]["content"]

    assert "Evidence First" in system_message
    assert "Output Schema Instructions" in system_message
    assert module.module_prompt[:40] in system_message
    assert "Confidence ceiling: moderate" in system_message


def test_prompt_compiler_metadata() -> None:
    registry = ModuleRegistry()
    compiler = PromptCompiler()
    module = registry.get("bias_epistemic_quality")
    bundle = _sample_bundle()

    compiled = compiler.compile_for_transcript(module, bundle)

    assert compiled.module_id == "bias_epistemic_quality"
    assert compiled.module_version == "1.0.0"
    assert compiled.compiler_version == COMPILER_VERSION
    assert compiled.shared_instructions_version == "1.0.0"
    assert compiled.output_schema_id == "module_output_v1"
    assert compiled.confidence_ceiling == Confidence.HIGH
    assert len(compiled.prompt_template_hash) == 64


def test_prompt_compiler_module_outputs_path() -> None:
    registry = ModuleRegistry()
    compiler = PromptCompiler()
    module = registry.get("meta_synthesis")

    compiled = compiler.compile_for_module_outputs(
        module,
        '{"module_id": "nvc_analysis", "executive_summary": "Test"}',
    )

    assert "Prior Module Outputs" in compiled.messages[1]["content"]
    assert "nvc_analysis" in compiled.messages[1]["content"]
    assert compiled.module_id == "meta_synthesis"
