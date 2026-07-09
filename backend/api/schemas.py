from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    ffmpeg_available: bool
    ollama_available: bool
    whisper_ready: bool


class TranscriptSegmentSchema(BaseModel):
    start: float
    end: float
    text: str


class TranscribeResponse(BaseModel):
    transcript: str
    segments: list[TranscriptSegmentSchema]
    language: str | None = None
    duration_seconds: float | None = None


class OllamaModelsResponse(BaseModel):
    models: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str


class PurposeSchema(BaseModel):
    id: str
    name: str
    description: str
    default_model: str | None = None


class PurposesResponse(BaseModel):
    purposes: list[PurposeSchema] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    transcript: str
    purpose_id: str
    model: str | None = None


class AnalyzeResponse(BaseModel):
    purpose_id: str
    purpose_name: str
    model: str
    analysis: str


class ProcessResponse(BaseModel):
    transcript: str
    segments: list[TranscriptSegmentSchema]
    language: str | None = None
    duration_seconds: float | None = None
    purpose_id: str
    purpose_name: str
    model: str
    analysis: str
