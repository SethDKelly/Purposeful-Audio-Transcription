"""Workflow DAG validation and topological expansion (v1.0 P2)."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field, model_validator


class WorkflowStepConfig(BaseModel):
    """One DAG step: a parallel group and/or a single synthesis module."""

    id: str
    depends_on: list[str] = Field(default_factory=list)
    parallel: list[str] = Field(default_factory=list)
    module: str | None = None

    @model_validator(mode="after")
    def _require_modules(self) -> WorkflowStepConfig:
        if not self.parallel and not self.module:
            raise ValueError(f"step {self.id}: must set parallel and/or module")
        if self.module and self.module in self.parallel:
            raise ValueError(f"step {self.id}: module also listed in parallel")
        return self

    def module_ids(self) -> list[str]:
        ids = list(self.parallel)
        if self.module:
            ids.append(self.module)
        return ids


@dataclass(frozen=True)
class WorkflowWave:
    step_id: str
    module_ids: list[str]
    is_synthesis: bool = False


def expand_steps_to_waves(steps: list[WorkflowStepConfig]) -> list[WorkflowWave]:
    """Topologically expand steps into execution waves; reject cycles / unknown deps."""
    if not steps:
        return []

    by_id = {step.id: step for step in steps}
    if len(by_id) != len(steps):
        raise ValueError("Duplicate workflow step ids")

    for step in steps:
        for dep in step.depends_on:
            if dep not in by_id:
                raise ValueError(f"step {step.id}: unknown depends_on {dep}")

    remaining = set(by_id)
    completed: set[str] = set()
    waves: list[WorkflowWave] = []

    while remaining:
        ready = [
            step_id
            for step_id in sorted(remaining)
            if set(by_id[step_id].depends_on).issubset(completed)
        ]
        if not ready:
            raise ValueError("Workflow steps contain a cycle or unsatisfiable depends_on")

        # Run independent ready steps as separate waves in stable id order
        # (keeps synthesis gates sequential when they share a dependency wave).
        for step_id in ready:
            step = by_id[step_id]
            if step.parallel:
                waves.append(
                    WorkflowWave(step_id=step_id, module_ids=list(step.parallel), is_synthesis=False)
                )
            if step.module:
                waves.append(
                    WorkflowWave(
                        step_id=f"{step_id}:module",
                        module_ids=[step.module],
                        is_synthesis=True,
                    )
                )
            remaining.remove(step_id)
            completed.add(step_id)

    return waves


def flatten_module_sequence(steps: list[WorkflowStepConfig] | None, modules: list[str]) -> list[str]:
    """Prefer steps when present; otherwise use linear modules list."""
    if steps:
        seq: list[str] = []
        for wave in expand_steps_to_waves(steps):
            seq.extend(wave.module_ids)
        return seq
    return list(modules)
