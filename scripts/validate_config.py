"""Validate RRE module/workflow YAML registries and cross-references.

Exit 0 when config is coherent; print errors and exit 1 otherwise.
Intended for pre-commit and CI (no AWS needed).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.module_registry import ModuleRegistry
from backend.core.ontology_registry import OntologyRegistry
from backend.core.workflow_registry import WorkflowRegistry
from backend.domain.enums import RelationshipType
from config.settings import settings


def validate() -> list[str]:
    errors: list[str] = []

    try:
        ontology = OntologyRegistry(ontology_dir=settings.ontology_dir)
    except Exception as exc:  # noqa: BLE001
        return [f"ontology registry failed to load: {exc}"]

    try:
        modules = ModuleRegistry(
            modules_dir=settings.modules_dir,
            prompts_dir=settings.prompts_dir,
            ontology=ontology,
        )
    except Exception as exc:  # noqa: BLE001 — surface load failures as script errors
        return [f"module registry failed to load: {exc}"]

    try:
        workflows = WorkflowRegistry(workflows_dir=settings.workflows_dir)
    except Exception as exc:  # noqa: BLE001
        return [f"workflow registry failed to load: {exc}"]

    modules_by_id = {
        module.config.id: module for module in modules.list_modules(enabled_only=False)
    }
    enabled_ids = {
        module.config.id for module in modules.list_modules(enabled_only=True)
    }

    if not modules_by_id:
        errors.append("no modules loaded from config/modules")
    if not workflows.list_workflows(enabled_only=False):
        errors.append("no workflows loaded from config/workflows")

    enum_relationships = {item.value for item in RelationshipType}
    missing_relationships = sorted(enum_relationships - ontology.relationship_ids)
    if missing_relationships:
        errors.append(
            "RelationshipType enum values missing from ontology: "
            + ", ".join(missing_relationships)
        )

    for module in modules_by_id.values():
        prompt_path = settings.prompts_dir / module.config.prompt_file
        if not prompt_path.is_file():
            errors.append(
                f"module {module.config.id}: prompt_file missing ({module.config.prompt_file})"
            )
        if module.config.input_type not in {"transcript", "module_outputs"}:
            errors.append(
                f"module {module.config.id}: unsupported input_type={module.config.input_type}"
            )

    for workflow in workflows.list_workflows(enabled_only=False):
        cfg = workflow.config
        sequence = workflow.module_sequence
        if not sequence:
            errors.append(f"workflow {cfg.id}: modules/steps resolve to empty sequence")
            continue

        for module_id in sequence:
            if module_id not in modules_by_id:
                errors.append(f"workflow {cfg.id}: unknown module_id {module_id}")
            elif module_id not in enabled_ids and cfg.enabled:
                errors.append(
                    f"workflow {cfg.id}: references disabled module {module_id}"
                )

        if cfg.steps:
            try:
                from backend.core.workflow_dag import expand_steps_to_waves

                expand_steps_to_waves(cfg.steps)
            except ValueError as exc:
                errors.append(f"workflow {cfg.id}: invalid steps DAG ({exc})")

        last = sequence[-1]
        has_meta = "meta_synthesis" in sequence
        if cfg.meta_synthesis and not has_meta:
            errors.append(
                f"workflow {cfg.id}: meta_synthesis=true but meta_synthesis not in modules"
            )
        if has_meta and last != "meta_synthesis":
            errors.append(
                f"workflow {cfg.id}: meta_synthesis must be the last module (found {last})"
            )
        if has_meta and not cfg.meta_synthesis:
            errors.append(
                f"workflow {cfg.id}: includes meta_synthesis but meta_synthesis flag is false"
            )

        for index, module_id in enumerate(sequence):
            module = modules_by_id.get(module_id)
            if module is None:
                continue
            if (
                module.config.input_type == "module_outputs"
                and index != len(sequence) - 1
            ):
                errors.append(
                    f"workflow {cfg.id}: module_outputs module {module_id} "
                    "must be last in the sequence"
                )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Config validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    ontology = OntologyRegistry(ontology_dir=settings.ontology_dir)
    module_count = len(
        ModuleRegistry(
            modules_dir=settings.modules_dir,
            prompts_dir=settings.prompts_dir,
        ).list_modules(enabled_only=False)
    )
    workflow_count = len(WorkflowRegistry().list_workflows(enabled_only=False))
    print(
        f"Config OK ({module_count} modules, {workflow_count} workflows, "
        f"{len(ontology.construct_ids)} constructs, "
        f"{len(ontology.relationship_ids)} relationships)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
