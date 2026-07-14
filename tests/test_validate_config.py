from scripts.validate_config import validate


def test_validate_config_passes_on_repo() -> None:
    assert validate() == []
