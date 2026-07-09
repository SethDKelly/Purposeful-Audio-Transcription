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
