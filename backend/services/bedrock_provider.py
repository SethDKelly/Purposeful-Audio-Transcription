"""Amazon Bedrock LLM provider for AWS deployment."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import time

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from backend.core.exceptions import LLMError
from backend.schemas.module_output_json_schema import MODULE_OUTPUT_V1_JSON_SCHEMA
from config.settings import settings

if TYPE_CHECKING:
    from backend.services.prompt_compiler import CompiledPrompt

logger = logging.getLogger(__name__)

# Module prompts can produce large structured JSON; botocore's default
# read timeout (~60s) is too short for Sonnet Converse on analysis modules.
_BEDROCK_CLIENT_CONFIG = Config(
    connect_timeout=10,
    read_timeout=600,
    retries={"max_attempts": 1, "mode": "standard"},
)

_JSON_OUTPUT_CONFIG = {
    "textFormat": {
        "type": "json_schema",
        "structure": {
            "jsonSchema": {
                "name": "module_output_v1",
                "description": "Structured RRE module analysis output",
                "schema": json.dumps(MODULE_OUTPUT_V1_JSON_SCHEMA),
            }
        },
    }
}

_JSON_SYSTEM_HINT = (
    "Your entire reply must be one JSON object matching module_output_v1. "
    "Do not use markdown fences. Do not write any prose before or after the JSON. "
    "Prefer structured findings/constructs; keep raw_markdown_report empty or very short."
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
        self.last_usage: dict[str, int] | None = None

    def health_check(self) -> bool:
        model_id = settings.resolved_bedrock_model_id
        if not model_id:
            return False
        # ALB/container probes call /api/health; never use the 600s Converse timeout.
        probe = Config(
            connect_timeout=2,
            read_timeout=3,
            retries={"max_attempts": 1, "mode": "standard"},
        )
        try:
            region = settings.resolved_aws_region
            control = boto3.client("bedrock", region_name=region, config=probe)
            if _is_inference_profile(model_id):
                control.get_inference_profile(inferenceProfileIdentifier=model_id)
            else:
                control.get_foundation_model(modelIdentifier=model_id)
            return True
        except (ClientError, BotoCoreError) as exc:
            logger.warning("Bedrock health check failed for %s: %s", model_id, exc)
            return False
        except Exception as exc:  # noqa: BLE001 — probe must never hang the health route
            logger.warning("Bedrock health check error for %s: %s", model_id, exc)
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
            request["system"] = (request.get("system") or []) + [{"text": _JSON_SYSTEM_HINT}]
            if settings.bedrock_structured_output:
                request["outputConfig"] = _JSON_OUTPUT_CONFIG

        return self._converse_with_fallback(request, json_mode=json_mode)

    def chat_cached(
        self,
        model: str,
        compiled: CompiledPrompt,
        *,
        json_mode: bool = False,
    ) -> str:
        """Converse with cache points on stable framework + shared user prefix.

        Layout (tools → system → messages):
        - system: shared framework, optional cachePoint
        - user content: evidence/priors, cachePoint, then module task

        Later modules on the same transcript can reuse the evidence prefix cache.
        """
        if not settings.bedrock_prompt_cache or not compiled.cache_user_prefix:
            return self.chat(model, compiled.messages, json_mode=json_mode)

        model_id = model or settings.resolved_bedrock_model_id
        if not model_id:
            raise LLMError("BEDROCK_MODEL_ID is not configured")

        cache_point = _cache_point()
        system: list[dict[str, Any]] = []
        if compiled.cache_system_text.strip():
            system.append({"text": compiled.cache_system_text})
            system.append(cache_point)
        if json_mode:
            system.append({"text": _JSON_SYSTEM_HINT})

        user_content: list[dict[str, Any]] = [
            {"text": compiled.cache_user_prefix},
            cache_point,
            {"text": compiled.cache_user_suffix},
        ]
        request: dict[str, Any] = {
            "modelId": model_id,
            "messages": [{"role": "user", "content": user_content}],
            "inferenceConfig": {
                "maxTokens": settings.bedrock_max_tokens,
                "temperature": 0.0,
            },
            "system": system,
        }
        if json_mode and settings.bedrock_structured_output:
            request["outputConfig"] = _JSON_OUTPUT_CONFIG

        try:
            return self._converse_with_fallback(request, json_mode=json_mode)
        except LLMError:
            # Cache point / TTL unsupported on some profiles — fall back to plain chat.
            logger.warning(
                "Bedrock prompt-cache converse failed; falling back to uncached chat",
                extra={"event": "bedrock.prompt_cache.fallback"},
            )
            return self.chat(model, compiled.messages, json_mode=json_mode)

    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        # Streaming spike deferred — module runs use non-streaming chat.
        yield self.chat(model, messages, json_mode=False)

    def _converse_with_fallback(
        self,
        request: dict[str, Any],
        *,
        json_mode: bool,
    ) -> str:
        try:
            started = time.perf_counter()
            response = self._converse(request)
            elapsed_ms = (time.perf_counter() - started) * 1000
        except (ClientError, BotoCoreError) as exc:
            if json_mode and "outputConfig" in request:
                logger.warning(
                    "Bedrock structured output failed (%s); retrying without outputConfig",
                    exc,
                )
                request = dict(request)
                request.pop("outputConfig", None)
                try:
                    started = time.perf_counter()
                    response = self._converse(request)
                    elapsed_ms = (time.perf_counter() - started) * 1000
                except (ClientError, BotoCoreError) as retry_exc:
                    raise LLMError(f"Bedrock converse failed: {retry_exc}") from retry_exc
            else:
                raise LLMError(f"Bedrock converse failed: {exc}") from exc

        usage = response.get("usage") or {}
        cache_read = int(usage.get("cacheReadInputTokens") or 0)
        cache_write = int(usage.get("cacheWriteInputTokens") or 0)
        input_tokens = int(usage.get("inputTokens") or 0)
        output_tokens = int(usage.get("outputTokens") or 0)
        self.last_usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_input_tokens": cache_read,
            "cache_write_input_tokens": cache_write,
            "latency_ms": int(elapsed_ms),
        }
        if cache_read or cache_write:
            logger.info(
                "Bedrock prompt cache usage read=%s write=%s",
                cache_read,
                cache_write,
                extra={
                    "event": "bedrock.prompt_cache.usage",
                    "cache_read_input_tokens": cache_read,
                    "cache_write_input_tokens": cache_write,
                },
            )

        stop_reason = response.get("stopReason")
        content = _extract_text(response)
        if not content:
            raise LLMError(
                f"Bedrock returned an empty response (stopReason={stop_reason!r})"
            )
        if stop_reason == "max_tokens":
            logger.warning(
                "Bedrock response truncated at max_tokens (%s); output length=%s",
                settings.bedrock_max_tokens,
                len(content),
            )
        return content

    def _converse(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._runtime.converse(**request)


def _cache_point() -> dict[str, Any]:
    ttl = (settings.bedrock_prompt_cache_ttl or "").strip()
    point: dict[str, Any] = {"cachePoint": {"type": "default"}}
    if ttl in {"5m", "1h"}:
        point["cachePoint"]["ttl"] = ttl
    return point


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
        elif role == "assistant":
            # Bedrock rejects empty assistant text blocks (repair turns).
            if not str(text).strip():
                conversation.append(
                    {
                        "role": "assistant",
                        "content": [{"text": "{}"}],
                    }
                )
            else:
                conversation.append({"role": "assistant", "content": [{"text": text}]})
        else:
            conversation.append({"role": role, "content": [{"text": text}]})
    return system, conversation


def _extract_text(response: dict[str, Any]) -> str:
    output = response.get("output") or {}
    message = output.get("message") or {}
    parts = message.get("content") or []
    texts: list[str] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        text = part.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text)
    return "".join(texts).strip()
