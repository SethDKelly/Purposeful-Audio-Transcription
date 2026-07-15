from unittest.mock import MagicMock, patch

import pytest

from backend.core.exceptions import LLMError
from backend.services.bedrock_provider import BedrockProvider


@pytest.fixture
def mock_bedrock_clients():
    with patch("backend.services.bedrock_provider.boto3.client") as mock_client:
        runtime = MagicMock()
        control = MagicMock()

        def _client(service_name, *args, **kwargs):
            if service_name == "bedrock-runtime":
                return runtime
            return control

        mock_client.side_effect = _client
        yield runtime, control


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_health_check(mock_settings, mock_bedrock_clients) -> None:
    _runtime, control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    control.get_foundation_model.return_value = {"modelDetails": {}}

    provider = BedrockProvider()
    assert provider.health_check() is True
    control.get_foundation_model.assert_called_once()


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_health_check_inference_profile(mock_settings, mock_bedrock_clients) -> None:
    _runtime, control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    control.get_inference_profile.return_value = {
        "inferenceProfileId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    }

    provider = BedrockProvider()
    assert provider.health_check() is True
    control.get_inference_profile.assert_called_once_with(
        inferenceProfileIdentifier="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    )
    control.get_foundation_model.assert_not_called()


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_uses_structured_output(mock_settings, mock_bedrock_clients) -> None:
    runtime, _control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    mock_settings.bedrock_max_tokens = 1024
    mock_settings.bedrock_structured_output = True
    mock_settings.bedrock_prompt_cache = False
    runtime.converse.return_value = {
        "stopReason": "end_turn",
        "output": {"message": {"content": [{"text": '{"findings": []}'}]}},
    }

    provider = BedrockProvider()
    text = provider.chat(
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Return JSON"},
        ],
        json_mode=True,
    )
    assert text.startswith("{")
    kwargs = runtime.converse.call_args.kwargs
    assert "outputConfig" in kwargs
    assert kwargs["outputConfig"]["textFormat"]["type"] == "json_schema"


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_cached_inserts_cache_points(mock_settings, mock_bedrock_clients) -> None:
    from backend.services.prompt_compiler import CompiledPrompt
    from backend.domain.enums import Confidence

    runtime, _control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    mock_settings.bedrock_max_tokens = 1024
    mock_settings.bedrock_structured_output = True
    mock_settings.bedrock_prompt_cache = True
    mock_settings.bedrock_prompt_cache_ttl = "1h"
    runtime.converse.return_value = {
        "stopReason": "end_turn",
        "usage": {"cacheWriteInputTokens": 5000, "cacheReadInputTokens": 0},
        "output": {"message": {"content": [{"text": '{"ok": true}'}]}},
    }

    compiled = CompiledPrompt(
        messages=[
            {"role": "system", "content": "shared"},
            {"role": "user", "content": "evidence\n\ntask"},
        ],
        module_id="nvc_analysis",
        module_version="1.0.0",
        compiler_version="1.2.0",
        shared_instructions_version="1.1.0",
        output_schema_id="module_output_v1",
        prompt_template_hash="a" * 64,
        confidence_ceiling=Confidence.MODERATE,
        cache_system_text="shared framework",
        cache_user_prefix="## Evidence Index\n\n[Q001] hi",
        cache_user_suffix="Analyze with NVC",
    )
    provider = BedrockProvider()
    text = provider.chat_cached(
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        compiled,
        json_mode=True,
    )
    assert text == '{"ok": true}'
    kwargs = runtime.converse.call_args.kwargs
    assert kwargs["system"][0]["text"] == "shared framework"
    assert kwargs["system"][1]["cachePoint"]["type"] == "default"
    assert kwargs["system"][1]["cachePoint"]["ttl"] == "1h"
    user_blocks = kwargs["messages"][0]["content"]
    assert user_blocks[0]["text"].startswith("## Evidence Index")
    assert user_blocks[1]["cachePoint"]["type"] == "default"
    assert user_blocks[2]["text"] == "Analyze with NVC"


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_falls_back_when_structured_output_rejected(
    mock_settings, mock_bedrock_clients
) -> None:
    from botocore.exceptions import ClientError

    runtime, _control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    mock_settings.bedrock_max_tokens = 1024
    mock_settings.bedrock_structured_output = True
    runtime.converse.side_effect = [
        ClientError(
            {"Error": {"Code": "ValidationException", "Message": "outputConfig unsupported"}},
            "Converse",
        ),
        {
            "stopReason": "end_turn",
            "output": {"message": {"content": [{"text": '{"ok": true}'}]}},
        },
    ]

    provider = BedrockProvider()
    text = provider.chat(
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        [{"role": "user", "content": "Return JSON"}],
        json_mode=True,
    )
    assert text == '{"ok": true}'
    assert runtime.converse.call_count == 2
    assert "outputConfig" not in runtime.converse.call_args_list[1].kwargs


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_skips_empty_assistant_blocks(mock_settings, mock_bedrock_clients) -> None:
    runtime, _control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    mock_settings.bedrock_max_tokens = 1024
    mock_settings.bedrock_structured_output = False
    runtime.converse.return_value = {
        "stopReason": "end_turn",
        "output": {"message": {"content": [{"text": '{"findings": []}'}]}},
    }

    provider = BedrockProvider()
    provider.chat(
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        [
            {"role": "user", "content": "x"},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "fix"},
        ],
        json_mode=False,
    )
    messages = runtime.converse.call_args.kwargs["messages"]
    assert messages[1]["content"][0]["text"] == "{}"


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_raises_llm_error(mock_settings, mock_bedrock_clients) -> None:
    runtime, _control = mock_bedrock_clients
    from botocore.exceptions import ClientError

    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    mock_settings.bedrock_max_tokens = 1024
    mock_settings.bedrock_structured_output = False
    runtime.converse.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "denied"}},
        "Converse",
    )

    provider = BedrockProvider()
    with pytest.raises(LLMError, match="Bedrock converse failed"):
        provider.chat(
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            [{"role": "user", "content": "hi"}],
        )
