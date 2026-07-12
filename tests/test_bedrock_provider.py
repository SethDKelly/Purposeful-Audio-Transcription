from unittest.mock import MagicMock, patch

import pytest

from backend.core.exceptions import LLMError
from backend.services.bedrock_provider import BedrockProvider


@pytest.fixture
def mock_bedrock_clients():
    with patch("backend.services.bedrock_provider.boto3.client") as mock_client:
        runtime = MagicMock()
        control = MagicMock()
        mock_client.side_effect = [runtime, control]
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
    control.get_inference_profile.return_value = {"inferenceProfileId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"}

    provider = BedrockProvider()
    assert provider.health_check() is True
    control.get_inference_profile.assert_called_once_with(
        inferenceProfileIdentifier="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    )
    control.get_foundation_model.assert_not_called()


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_returns_text(mock_settings, mock_bedrock_clients) -> None:
    runtime, control = mock_bedrock_clients
    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    mock_settings.bedrock_max_tokens = 1024
    runtime.converse.return_value = {
        "output": {"message": {"content": [{"text": '{"findings": []}'}]}}
    }

    provider = BedrockProvider()
    text = provider.chat(
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Return JSON"},
        ],
        json_mode=True,
    )
    assert text.startswith("{")
    runtime.converse.assert_called_once()


@patch("backend.services.bedrock_provider.settings")
def test_bedrock_chat_raises_llm_error(mock_settings, mock_bedrock_clients) -> None:
    runtime, _control = mock_bedrock_clients
    from botocore.exceptions import ClientError

    mock_settings.resolved_aws_region = "us-east-2"
    mock_settings.resolved_bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    mock_settings.bedrock_max_tokens = 1024
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
