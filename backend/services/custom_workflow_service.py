"""Build and register ephemeral custom workflow definitions (v1.0 P3)."""

from __future__ import annotations

import re

from backend.core.exceptions import CustomWorkflowValidationError
from backend.core.module_registry import ModuleRegistry, module_registry
from backend.core.workflow_dag import WorkflowStepConfig, expand_steps_to_waves
from backend.core.workflow_registry import WorkflowConfig, WorkflowDefinition, workflow_registry
from backend.services.safety_risk_scanner import SKIP_IN_SAFETY_MODE

META_SYNTHESIS_ID = "meta_synthesis"


class CustomWorkflowService:
    def __init__(
        self,
        modules: ModuleRegistry | None = None,
        workflows=workflow_registry,
    ) -> None:
        self._modules = modules or module_registry
        self._workflows = workflows

    def build_definition(
        self,
        *,
        modules: list[str],
        name: str | None = None,
        steps: list[WorkflowStepConfig] | None = None,
        safety_mode: bool = False,
    ) -> tuple[WorkflowDefinition, str]:
        if steps:
            module_ids = _module_ids_from_steps(steps)
            if modules:
                if set(modules) != set(module_ids):
                    raise CustomWorkflowValidationError(
                        "When steps are provided, modules must match step module ids"
                    )
            else:
                modules = module_ids
        if safety_mode:
            modules = [m for m in modules if m not in SKIP_IN_SAFETY_MODE]
            if steps:
                steps = _filter_steps_for_safety(steps)
        self._validate_modules(modules)

        workflow_id = self._workflow_id(name)
        config = WorkflowConfig(
            id=workflow_id,
            name=name or "Custom workflow",
            version="1.0.0",
            enabled=True,
            description="User-defined module suite",
            estimated_runtime="varies",
            modules=[] if steps else list(modules),
            steps=list(steps or []),
            meta_synthesis=META_SYNTHESIS_ID in modules,
            default_background=False,
        )
        definition = WorkflowDefinition(config=config)
        self._workflows.register_ephemeral(definition)
        return definition, workflow_id

    def _validate_modules(self, modules: list[str]) -> None:
        if not modules:
            raise CustomWorkflowValidationError("Custom workflow requires at least one module")
        seen: set[str] = set()
        for module_id in modules:
            if module_id in seen:
                raise CustomWorkflowValidationError(f"Duplicate module: {module_id}")
            seen.add(module_id)
            self._modules.get(module_id)

        if META_SYNTHESIS_ID in modules and modules[-1] != META_SYNTHESIS_ID:
            raise CustomWorkflowValidationError(
                f"{META_SYNTHESIS_ID} must be the last module when included"
            )

    def _workflow_id(self, name: str | None) -> str:
        if not name or not name.strip():
            return "custom"
        slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
        if not slug:
            return "custom"
        return f"custom:{slug[:32]}"


def _filter_steps_for_safety(steps: list[WorkflowStepConfig]) -> list[WorkflowStepConfig]:
    filtered: list[WorkflowStepConfig] = []
    for step in steps:
        parallel = [m for m in step.parallel if m not in SKIP_IN_SAFETY_MODE]
        module = step.module if step.module not in SKIP_IN_SAFETY_MODE else None
        if not parallel and not module:
            continue
        filtered.append(
            WorkflowStepConfig(
                id=step.id,
                depends_on=list(step.depends_on),
                parallel=parallel,
                module=module,
            )
        )
    if not filtered:
        raise CustomWorkflowValidationError("No modules remain after safety_mode filtering")
    return filtered


def _module_ids_from_steps(steps: list[WorkflowStepConfig]) -> list[str]:
    expand_steps_to_waves(steps)
    ids: list[str] = []
    for step in steps:
        ids.extend(step.module_ids())
    return ids


custom_workflow_service = CustomWorkflowService()
