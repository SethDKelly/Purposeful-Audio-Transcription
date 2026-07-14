"""Load and validate analysis module definitions from YAML."""

from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from backend.core.exceptions import ModuleNotFoundError
from backend.domain.enums import AnalyticalLevel, Confidence
from config.settings import settings


class ModuleConfig(BaseModel):
    id: str
    name: str
    version: str
    enabled: bool = True
    description: str = ""
    primary_lens: str
    analytical_level: AnalyticalLevel
    unit_of_analysis: str
    primary_question: str
    secondary_questions: list[str] = Field(default_factory=list)
    required_constructs: list[str] = Field(default_factory=list)
    output_schema: str = "module_output_v1"
    recommended_companions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    inference_depth: str = "medium"
    confidence_ceiling: Confidence = Confidence.MODERATE
    prompt_file: str
    ollama_model: str | None = None
    model_id: str | None = None
    input_type: str = "transcript"

    @property
    def resolved_model_id(self) -> str | None:
        return self.model_id or self.ollama_model


@dataclass(frozen=True)
class AnalysisModule:
    config: ModuleConfig
    module_prompt: str


class ModuleRegistry:
    def __init__(
        self,
        modules_dir: Path | None = None,
        prompts_dir: Path | None = None,
    ) -> None:
        self._modules_dir = modules_dir or settings.modules_dir
        self._prompts_dir = prompts_dir or settings.prompts_dir
        self._modules = self._load()

    def _load_prompt_file(self, filename: str) -> str:
        prompt_path = self._prompts_dir / filename
        if not prompt_path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8").strip()

    def _load_module_file(self, path: Path) -> AnalysisModule:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            config = ModuleConfig.model_validate(raw)
        except ValidationError as exc:
            raise ValueError(f"Invalid module config {path.name}: {exc}") from exc

        return AnalysisModule(
            config=config,
            module_prompt=self._load_prompt_file(config.prompt_file),
        )

    def _load(self) -> dict[str, AnalysisModule]:
        if not self._modules_dir.is_dir():
            return {}

        loaded: dict[str, AnalysisModule] = {}
        for path in sorted(self._modules_dir.glob("*.yaml")):
            module = self._load_module_file(path)
            loaded[module.config.id] = module
        return loaded

    def reload(self) -> None:
        self._modules = self._load()

    def list_modules(self, enabled_only: bool = True) -> list[AnalysisModule]:
        modules = list(self._modules.values())
        if enabled_only:
            modules = [module for module in modules if module.config.enabled]
        return sorted(modules, key=lambda module: module.config.name.lower())

    def get(self, module_id: str) -> AnalysisModule:
        module = self._modules.get(module_id)
        if module is None:
            raise ModuleNotFoundError(f"Unknown module: {module_id}")
        if not module.config.enabled:
            raise ModuleNotFoundError(f"Module is disabled: {module_id}")
        return module

    def has(self, module_id: str) -> bool:
        module = self._modules.get(module_id)
        return module is not None and module.config.enabled


module_registry = ModuleRegistry()
