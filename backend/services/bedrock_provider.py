"""Amazon Bedrock LLM provider for AWS deployment."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from backend.core.exceptions import LLMError
from config.settings import settings

logger = logging.getLogger(__name__)

# Module prompts can produce large structured JSON; botocore's default
# read timeout (~60s) is too short for Sonnet Converse on analysis modules.
_BEDROCK_CLIENT_CONFIG = Config(
    connect_timeout=10,
    read_timeout=300,
    retries={"max_attempts": 2, "mode": "standard"},
)


class BedrockProvider:
    name = "bedrock"

    def __init__(self) -> None:
        region = settings.resolved_aws_region
        self._runtime = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=_BEDROCK_CLIENT_CONFIG,
        )
        self._control = boto3.client(
            "bedrock",
            region_name=region,
            config=_BEDROCK_CLIENT_CONFIG,
        )

    def health_check(self) -> bool:
        model_id = settings.resolved_bedrock_model_id
        if not model_id:
            return False
        try:
            if _is_inference_profile(model_id):
                self._control.get_inference_profile(inferenceProfileIdentifier=model_id)
            else:
                self._control.get_foundation_model(modelIdentifier=model_id)
            return True
        except (ClientError, BotoCoreError) as exc:
            logger.warning("Bedrock health check failed for %s: %s", model_id, exc)
            return False

    def list_models(self) -> list[str]:
        model_id = settings.resolved_bedrock_model_id
        return [model_id] if model_id else []

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        json_mode: bool = False,
    ) -> str:
        model_id = model or settings.resolved_bedrock_model_id
        if not model_id:
            raise LLMError("BEDROCK_MODEL_ID is not configured")

        system_blocks, conversation = _split_messages(messages)
        request: dict[str, Any] = {
            "modelId": model_id,
            "messages": conversation,
            "inferenceConfig": {
                "maxTokens": settings.bedrock_max_tokens,
                "temperature": 0.0,
            },
        }
        if system_blocks:
            request["system"] = system_blocks
        if json_mode:
            request["system"] = (request.get("system") or []) + [
                {
                    "text": (
                        "Respond with a single valid JSON object only. "
                        "Do not wrap the JSON in markdown fences."
                    )
                }
            ]

        try:
            response = self._runtime.converse(**request)
        except (ClientError, BotoCoreError) as exc:
            raise LLMError(f"Bedrock converse failed: {exc}") from exc

        content = _extract_text(response)
        if not content:
            raise LLMError("Bedrock returned an empty response")
        return content

    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        # Streaming spike deferred — module runs use non-streaming chat.
        yield self.chat(model, messages, json_mode=False)


def _is_inference_profile(model_id: str) -> bool:
    return model_id.startswith(("us.", "global.", "eu.", "ap.")) or "inference-profile/" in model_id


def _split_messages(
    messages: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    system: list[dict[str, str]] = []
    conversation: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role", "user")
        text = message.get("content", "")
        if role == "system":
            system.append({"text": text})
        else:
            conversation.append({"role": role, "content": [{"text": text}]})
    return system, conversation


def _extract_text(response: dict[str, Any]) -> str:
    output = response.get("output") or {}
    message = output.get("message") or {}
    parts = message.get("content") or []
    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    return "".join(texts).strip()
