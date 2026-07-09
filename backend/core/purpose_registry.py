"""Load analysis purposes and their prompt files."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from config.settings import settings
from backend.core.exceptions import PurposeNotFoundError


@dataclass(frozen=True)
class Purpose:
    id: str
    name: str
    description: str
    enabled: bool
    ollama_model: str | None
    system_prompt: str
    user_prompt_template: str


class PurposeRegistry:
    def __init__(
        self,
        purposes_path: Path | None = None,
        prompts_dir: Path | None = None,
    ) -> None:
        self._purposes_path = purposes_path or settings.purposes_file
        self._prompts_dir = prompts_dir or settings.prompts_dir
        self._purposes = self._load()

    def _load_prompt_file(self, filename: str) -> str:
        prompt_path = self._prompts_dir / filename
        if not prompt_path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8").strip()

    def _load(self) -> dict[str, Purpose]:
        if not self._purposes_path.is_file():
            return {}

        raw = yaml.safe_load(self._purposes_path.read_text(encoding="utf-8")) or {}
        purposes_data = raw.get("purposes", {})
        loaded: dict[str, Purpose] = {}

        for purpose_id, config in purposes_data.items():
            if not isinstance(config, dict):
                continue

            prompt_file = config.get("system_prompt_file")
            if not prompt_file:
                continue

            loaded[purpose_id] = Purpose(
                id=purpose_id,
                name=config.get("name", purpose_id),
                description=config.get("description", "").strip(),
                enabled=bool(config.get("enabled", False)),
                ollama_model=config.get("ollama_model") or None,
                system_prompt=self._load_prompt_file(prompt_file),
                user_prompt_template=config.get("user_prompt_template", "{transcript}"),
            )

        return loaded

    def reload(self) -> None:
        self._purposes = self._load()

    def list_purposes(self, enabled_only: bool = True) -> list[Purpose]:
        purposes = list(self._purposes.values())
        if enabled_only:
            purposes = [purpose for purpose in purposes if purpose.enabled]
        return sorted(purposes, key=lambda purpose: purpose.name.lower())

    def get(self, purpose_id: str) -> Purpose:
        purpose = self._purposes.get(purpose_id)
        if purpose is None:
            raise PurposeNotFoundError(f"Unknown purpose: {purpose_id}")
        if not purpose.enabled:
            raise PurposeNotFoundError(f"Purpose is disabled: {purpose_id}")
        return purpose

    def build_messages(self, purpose_id: str, transcript: str) -> list[dict[str, str]]:
        purpose = self.get(purpose_id)
        user_content = purpose.user_prompt_template.format(transcript=transcript)
        return [
            {"role": "system", "content": purpose.system_prompt},
            {"role": "user", "content": user_content},
        ]


purpose_registry = PurposeRegistry()
