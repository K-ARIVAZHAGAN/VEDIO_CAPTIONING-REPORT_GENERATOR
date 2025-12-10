"""
Custom exception classes for the Meeting Video Captioning application.

This module defines a hierarchy of custom exceptions to provide clear,
specific error handling throughout the application.
"""

from typing import Optional


class MeetingCaptioningError(Exception):
    """
    Base exception class for all Meeting Captioning errors.
    
    All custom exceptions in the application should inherit from this class.
    """
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            original_error: Original exception that caused this error (if any)
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.original_error:
            return f"{self.message} (caused by: {str(self.original_error)})"
        return self.message


class VideoLoadError(MeetingCaptioningError):
    """
    Exception raised when video loading or downloading fails.
    
    This includes errors from:
    - Invalid file paths
    - Unsupported video formats
    - Failed YouTube downloads
    - Network errors when accessing web videos
    - Authentication failures for private videos
    """
    pass


class TranscriptionError(MeetingCaptioningError):
    """
    Exception raised when audio transcription fails.
    
    This includes errors from:
    - Audio extraction failures
    - Speech-to-text engine errors
    - Unsupported audio formats
    - Low-quality audio that cannot be transcribed
    """
    pass


class ProcessingError(MeetingCaptioningError):
    """
    Exception raised during video processing operations.
    
    This includes errors from:
    - Scene detection failures
    - Frame extraction issues
    - Caption generation errors
    - Video encoding problems
    """
    pass


class ReportGenerationError(MeetingCaptioningError):
    """
    Exception raised when report generation fails.
    
    This includes errors from:
    - PDF/DOCX/TXT export failures
    - File I/O errors
    - Template rendering issues
    - Missing or invalid report data
    """
    pass


class ConfigurationError(MeetingCaptioningError):
    """
    Exception raised for configuration-related errors.
    
    This includes errors from:
    - Invalid configuration values
    - Missing required settings
    - Environment variable issues
    """
    pass


class ValidationError(MeetingCaptioningError):
    """
    Exception raised for input validation errors.
    
    This includes errors from:
    - Invalid input parameters
    - Out-of-range values
    - Type mismatches
    """
    pass
