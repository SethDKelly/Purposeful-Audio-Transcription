"""Lightweight tooling checks (AWS product has no local Whisper/Ollama server)."""

import sys

from config.settings import settings


def check_python_version() -> bool:
    ok = sys.version_info >= (3, 11)
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] Python 3.11+ (current: {sys.version.split()[0]})")
    return ok


def check_imports() -> bool:
    try:
        import fastapi  # noqa: F401
        import boto3  # noqa: F401
        import sqlalchemy  # noqa: F401
    except ImportError as exc:
        print(f"  [FAIL] Core imports: {exc}")
        return False
    print("  [OK] Core packages (fastapi, boto3, sqlalchemy)")
    return True


def main() -> int:
    print("RRE developer tooling check")
    print(f"  LLM default provider setting: {settings.llm_provider}")
    print(f"  ASR default provider setting: {settings.transcription_provider}")
    ok = check_python_version() and check_imports()
    if ok:
        print("\nTooling OK. Validate the app on AWS after Deploy.")
        return 0
    print("\nTooling check failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
