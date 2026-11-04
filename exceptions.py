class CVTError(Exception):
    """Base exception class for CVT application."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class ConfigurationError(CVTError):
    """Raised when there's a configuration issue."""
    pass

class VideoProcessingError(CVTError):
    """Raised when there's an error in video processing."""
    pass

class FrameProcessingError(CVTError):
    """Raised when there's an error in frame processing."""
    pass

class ProcessorNotFoundError(CVTError):
    """Raised when a requested processor implementation is not found."""
    pass