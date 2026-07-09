class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AudioValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class WhisperError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class OllamaError(AppError):
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


class ModuleNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ModuleRunNotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ModuleRunError(AppError):
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
