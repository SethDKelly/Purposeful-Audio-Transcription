class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AudioValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class TranscriptionError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


# Backward-compatible alias
WhisperError = TranscriptionError


class LLMError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class PurposeNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class AnalysisError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class TranscriptNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class TranscriptValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class TranscriptNotReadyError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class CaseNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class CaseValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ModuleNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ModuleRunNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ModuleRunError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class CustomWorkflowValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class WorkflowNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class WorkflowRunNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class WorkflowRunError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class WorkflowRunCancelled(WorkflowRunError):
    """Cooperative cancel of an in-flight or queued workflow run."""


class WorkflowRunTimeout(WorkflowRunError):
    """Workflow job exceeded WORKFLOW_JOB_TIMEOUT_SECONDS."""


class WorkflowSyncLimitError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class SynthesisNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class SynthesisError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class FindingNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ExplorationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
