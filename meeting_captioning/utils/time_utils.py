"""
Time utility functions for timestamp formatting and time conversions.

This module provides utilities for working with timestamps, durations,
and time-based formatting for captions and reports.
"""

from datetime import datetime, timedelta
from typing import Union, Tuple


def seconds_to_hms(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format.
    
    Args:
        seconds: Time in seconds (can be float)
        
    Returns:
        Formatted time string (HH:MM:SS)
        
    Examples:
        >>> seconds_to_hms(90)
        '00:01:30'
        >>> seconds_to_hms(3661.5)
        '01:01:01'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def seconds_to_hms_ms(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS.mmm format with milliseconds.
    
    Args:
        seconds: Time in seconds (float)
        
    Returns:
        Formatted time string (HH:MM:SS.mmm)
        
    Examples:
        >>> seconds_to_hms_ms(90.5)
        '00:01:30.500'
        >>> seconds_to_hms_ms(3661.123)
        '01:01:01.123'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def hms_to_seconds(time_str: str) -> float:
    """
    Convert HH:MM:SS or HH:MM:SS.mmm format to seconds.
    
    Args:
        time_str: Time string in format HH:MM:SS or HH:MM:SS.mmm
        
    Returns:
        Time in seconds
        
    Examples:
        >>> hms_to_seconds("00:01:30")
        90.0
        >>> hms_to_seconds("01:01:01.500")
        3661.5
    """
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    
    # Handle optional milliseconds
    if '.' in parts[2]:
        secs_parts = parts[2].split('.')
        seconds = int(secs_parts[0])
        milliseconds = int(secs_parts[1])
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    else:
        seconds = int(parts[2])
        total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return float(total_seconds)


def format_timestamp(
    seconds: float,
    include_ms: bool = False,
    format_type: str = "hms"
) -> str:
    """
    Format a timestamp in various formats.
    
    Args:
        seconds: Time in seconds
        include_ms: Whether to include milliseconds
        format_type: Format type ("hms", "readable", "srt")
            - "hms": HH:MM:SS or HH:MM:SS.mmm
            - "readable": "X hours Y minutes Z seconds"
            - "srt": HH:MM:SS,mmm (SRT subtitle format)
        
    Returns:
        Formatted timestamp string
        
    Examples:
        >>> format_timestamp(3661.5, include_ms=True)
        '01:01:01.500'
        >>> format_timestamp(90, format_type="readable")
        '1 minute 30 seconds'
        >>> format_timestamp(3661.5, include_ms=True, format_type="srt")
        '01:01:01,500'
    """
    if format_type == "hms":
        return seconds_to_hms_ms(seconds) if include_ms else seconds_to_hms(seconds)
    
    elif format_type == "readable":
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs > 0 or not parts:
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")
        
        return " ".join(parts)
    
    elif format_type == "srt":
        # SRT format uses comma for milliseconds
        hms = seconds_to_hms_ms(seconds)
        return hms.replace('.', ',')
    
    else:
        raise ValueError(f"Unknown format_type: {format_type}")


def format_duration(start_seconds: float, end_seconds: float) -> str:
    """
    Format a duration range as "HH:MM:SS - HH:MM:SS".
    
    Args:
        start_seconds: Start time in seconds
        end_seconds: End time in seconds
        
    Returns:
        Formatted duration string
        
    Example:
        >>> format_duration(60, 150)
        '00:01:00 - 00:02:30'
    """
    start = seconds_to_hms(start_seconds)
    end = seconds_to_hms(end_seconds)
    return f"{start} - {end}"


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        Current timestamp as string
        
    Example:
        >>> get_current_timestamp()
        '2025-12-08T14:30:45.123456'
    """
    return datetime.now().isoformat()


def parse_timedelta(time_str: str) -> float:
    """
    Parse various time string formats to seconds.
    
    Supports:
    - "HH:MM:SS" or "HH:MM:SS.mmm"
    - "MM:SS"
    - "XXs" (seconds)
    - "XXm" (minutes)
    - "XXh" (hours)
    
    Args:
        time_str: Time string in various formats
        
    Returns:
        Time in seconds
        
    Examples:
        >>> parse_timedelta("01:30:00")
        5400.0
        >>> parse_timedelta("90s")
        90.0
        >>> parse_timedelta("1.5h")
        5400.0
    """
    time_str = time_str.strip()
    
    # Handle HH:MM:SS format
    if ':' in time_str:
        return hms_to_seconds(time_str)
    
    # Handle suffix format (s, m, h)
    if time_str.endswith('s'):
        return float(time_str[:-1])
    elif time_str.endswith('m'):
        return float(time_str[:-1]) * 60
    elif time_str.endswith('h'):
        return float(time_str[:-1]) * 3600
    
    # Default: assume seconds
    return float(time_str)


def create_time_ranges(
    total_duration: float,
    segment_duration: float
) -> list[Tuple[float, float]]:
    """
    Create time ranges for splitting a duration into segments.
    
    Args:
        total_duration: Total duration in seconds
        segment_duration: Duration of each segment in seconds
        
    Returns:
        List of (start, end) tuples representing time ranges
        
    Example:
        >>> create_time_ranges(100, 30)
        [(0, 30), (30, 60), (60, 90), (90, 100)]
    """
    ranges = []
    current = 0.0
    
    while current < total_duration:
        end = min(current + segment_duration, total_duration)
        ranges.append((current, end))
        current = end
    
    return ranges
