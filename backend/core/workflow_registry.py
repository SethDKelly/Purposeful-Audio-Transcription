"""Load and validate workflow definitions from YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from backend.core.exceptions import WorkflowNotFoundError
from backend.core.workflow_dag import (
    WorkflowStepConfig,
    WorkflowWave,
    expand_steps_to_waves,
    flatten_module_sequence,
)
from config.settings import settings


class WorkflowConfig(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    description: str = ""
    estimated_runtime: str = ""
    recommended_model: str | None = None
    output_tone: str = ""
    modules: list[str] = Field(default_factory=list)
    steps: list[WorkflowStepConfig] = Field(default_factory=list)
    meta_synthesis: bool = False
    default_background: bool = False

    @model_validator(mode="after")
    def _require_modules_or_steps(self) -> WorkflowConfig:
        if not self.modules and not self.steps:
            raise ValueError("workflow must define modules or steps")
        if self.steps:
            # Validate DAG early so registry load fails loud.
            expand_steps_to_waves(self.steps)
        return self


@dataclass(frozen=True)
class WorkflowDefinition:
    config: WorkflowConfig

    @property
    def module_sequence(self) -> list[str]:
        return flatten_module_sequence(self.config.steps or None, self.config.modules)

    @property
    def waves(self) -> list[WorkflowWave] | None:
        if not self.config.steps:
            return None
        return expand_steps_to_waves(self.config.steps)


class WorkflowRegistry:
    def __init__(self, workflows_dir: Path | None = None) -> None:
        self._workflows_dir = workflows_dir or settings.workflows_dir
        self._workflows = self._load()
        self._ephemeral: dict[str, WorkflowDefinition] = {}

    def _load_file(self, path: Path) -> WorkflowDefinition:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            config = WorkflowConfig.model_validate(raw)
        except ValidationError as exc:
            raise ValueError(f"Invalid workflow config {path.name}: {exc}") from exc
        return WorkflowDefinition(config=config)

    def _load(self) -> dict[str, WorkflowDefinition]:
        if not self._workflows_dir.is_dir():
            return {}

        loaded: dict[str, WorkflowDefinition] = {}
        for path in sorted(self._workflows_dir.glob("*.yaml")):
            workflow = self._load_file(path)
            loaded[workflow.config.id] = workflow
        return loaded

    def reload(self) -> None:
        self._workflows = self._load()
        self._ephemeral.clear()

    def register_ephemeral(self, definition: WorkflowDefinition) -> None:
        self._ephemeral[definition.config.id] = definition

    def unregister_ephemeral(self, workflow_id: str) -> None:
        self._ephemeral.pop(workflow_id, None)

    def list_workflows(self, enabled_only: bool = True) -> list[WorkflowDefinition]:
        workflows = list(self._workflows.values())
        if enabled_only:
            workflows = [workflow for workflow in workflows if workflow.config.enabled]
        return sorted(workflows, key=lambda workflow: workflow.config.name.lower())

    def get(self, workflow_id: str) -> WorkflowDefinition:
        workflow = self._ephemeral.get(workflow_id) or self._workflows.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(f"Unknown workflow: {workflow_id}")
        if not workflow.config.enabled:
            raise WorkflowNotFoundError(f"Workflow is disabled: {workflow_id}")
        return workflow


workflow_registry = WorkflowRegistry()
