from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from backend.core.exceptions import OllamaError
from backend.services.ollama_service import OllamaService


def _response(*, content: str = "", thinking: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        message=SimpleNamespace(content=content or None, thinking=thinking or None),
        done_reason="stop",
        eval_count=1,
    )


@patch("backend.services.ollama_service.ollama.Client")
@patch("backend.services.ollama_service.settings")
def test_chat_passes_think_false_by_default(mock_settings, mock_client_cls) -> None:
    mock_settings.ollama_think = False
    client = MagicMock()
    mock_client_cls.return_value = client
    client.chat.return_value = _response(content='{"ok": true}')
    service = OllamaService()

    result = service.chat("gemma4:12b", [{"role": "user", "content": "hi"}])

    assert result == '{"ok": true}'
    client.chat.assert_called_once_with(
        model="gemma4:12b",
        messages=[{"role": "user", "content": "hi"}],
        think=False,
    )


@patch("backend.services.ollama_service.ollama.Client")
@patch("backend.services.ollama_service.settings")
def test_chat_retries_without_thinking_when_content_empty(mock_settings, mock_client_cls) -> None:
    mock_settings.ollama_think = True
    client = MagicMock()
    mock_client_cls.return_value = client
    client.chat.side_effect = [
        _response(content="", thinking="long internal reasoning"),
        _response(content='{"ok": true}'),
    ]
    service = OllamaService()

    result = service.chat("gemma4:12b", [{"role": "user", "content": "hi"}])

    assert result == '{"ok": true}'
    assert client.chat.call_count == 2
    assert client.chat.call_args_list[1].kwargs["think"] is False


@patch("backend.services.ollama_service.ollama.Client")
@patch("backend.services.ollama_service.settings")
def test_chat_raises_helpful_error_when_thinking_consumes_budget(
    mock_settings, mock_client_cls
) -> None:
    mock_settings.ollama_think = False
    client = MagicMock()
    mock_client_cls.return_value = client
    client.chat.return_value = _response(content="", thinking="only thinking")
    service = OllamaService()

    with pytest.raises(OllamaError, match="thinking field"):
        service.chat("gemma4:12b", [{"role": "user", "content": "hi"}])


@patch("backend.services.ollama_service.ollama.Client")
@patch("backend.services.ollama_service.settings")
def test_chat_stream_passes_think_false(mock_settings, mock_client_cls) -> None:
    mock_settings.ollama_think = False
    client = MagicMock()
    mock_client_cls.return_value = client
    client.chat.return_value = [
        SimpleNamespace(message=SimpleNamespace(content="hel")),
        SimpleNamespace(message=SimpleNamespace(content="lo")),
    ]
    service = OllamaService()

    chunks = list(service.chat_stream("gemma4:12b", [{"role": "user", "content": "hi"}]))

    assert chunks == ["hel", "lo"]
    client.chat.assert_called_once_with(
        model="gemma4:12b",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
        think=False,
    )
