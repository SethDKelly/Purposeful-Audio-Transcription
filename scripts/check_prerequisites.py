"""Verify external prerequisites for Purposeful Audio Transcription."""

import shutil
import sys

import httpx

from config.settings import settings


def check_python_version() -> bool:
    ok = sys.version_info >= (3, 11)
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] Python 3.11+ (current: {sys.version.split()[0]})")
    return ok


def check_ffmpeg() -> bool:
    ok = shutil.which("ffmpeg") is not None
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] ffmpeg on PATH")
    if not ok:
        print("         Install: https://ffmpeg.org/download.html")
    return ok


def check_ollama() -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings.ollama_host}/api/tags")
            ok = response.status_code == 200
    except httpx.HTTPError:
        ok = False

    status = "OK" if ok else "FAIL"
    print(f"  [{status}] Ollama running at {settings.ollama_host}")
    if not ok:
        print("         Start Ollama and run: ollama serve")
    return ok


def check_ollama_models() -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings.ollama_host}/api/tags")
            if response.status_code != 200:
                print("  [SKIP] Ollama models (Ollama not reachable)")
                return False
            data = response.json()
            models = data.get("models", [])
            ok = len(models) > 0
            status = "OK" if ok else "WARN"
            names = [m.get("name", "?") for m in models]
            print(f"  [{status}] Ollama models pulled: {', '.join(names) or 'none'}")
            if not ok:
                print("         Pull a model: ollama pull llama3.2")
            return ok
    except httpx.HTTPError:
        print("  [SKIP] Ollama models (Ollama not reachable)")
        return False


def check_whisper_model() -> bool:
    print(f"  [INFO] Whisper model configured: {settings.whisper_model}")
    print(f"  [INFO] Whisper device: {settings.whisper_device}")
    print(f"  [INFO] Whisper compute type: {settings.whisper_compute_type}")
    print("         Model downloads automatically on first transcription.")
    return True


def check_temp_dir() -> bool:
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"  [OK] Temp directory: {settings.temp_dir.resolve()}")
    return True


def main() -> int:
    print("Purposeful Audio Transcription - Prerequisites Check\n")

    checks = [
        check_python_version(),
        check_ffmpeg(),
        check_ollama(),
        check_ollama_models(),
        check_whisper_model(),
        check_temp_dir(),
    ]

    print()
    required = checks[:3]
    if all(required):
        print("Required prerequisites met. You can start the API:")
        print("  uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
        return 0

    print("Some required prerequisites are missing. Fix the [FAIL] items above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
