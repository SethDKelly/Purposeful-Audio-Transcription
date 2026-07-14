# RRE API — full local image (Whisper + pyannote + ffmpeg).
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY config ./config
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[local]"

ENV API_HOST=0.0.0.0 \
    API_PORT=8000 \
    LOG_JSON=true \
    PYTHONUNBUFFERED=1 \
    TRANSCRIPTION_PROVIDER=whisper \
    DIARIZATION_ENABLED=true \
    ALEMBIC_AUTO_UPGRADE=true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD curl -f "http://127.0.0.1:8000/api/live" || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
