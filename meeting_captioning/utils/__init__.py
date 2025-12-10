"""Utils package for shared utilities."""

from meeting_captioning.utils.logging_config import setup_logging
from meeting_captioning.utils.time_utils import format_timestamp, seconds_to_hms
from meeting_captioning.utils.error_handling import (
    MeetingCaptioningError,
    VideoLoadError,
    TranscriptionError,
    ProcessingError,
    ReportGenerationError
)

__all__ = [
    "setup_logging",
    "format_timestamp",
    "seconds_to_hms",
    "MeetingCaptioningError",
    "VideoLoadError",
    "TranscriptionError",
    "ProcessingError",
    "ReportGenerationError"
]
