from unittest.mock import MagicMock

from ui.api_client import _raise_for_status


def test_raise_for_status_reads_streaming_error_body() -> None:
    response = MagicMock()
    response.status_code = 404
    response.read.return_value = b'{"detail":"Not Found"}'
    response.json.return_value = {"detail": "Not Found"}
    response.text = "Not Found"

    try:
        _raise_for_status(response)
    except RuntimeError as exc:
        assert str(exc) == "Not Found"
    else:
        raise AssertionError("Expected RuntimeError")

    response.read.assert_called_once()
