"""
Logging configuration module for the Meeting Video Captioning application.

This module sets up structured logging with appropriate handlers, formatters,
and log levels. It supports both file and console logging with rotation.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

from meeting_captioning.config import Config


def setup_logging(
    name: str = "meeting_captioning",
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up and configure logging for the application.
    
    Creates a logger with both console and file handlers. File logs are rotated
    when they reach 10MB, keeping up to 5 backup files.
    
    Args:
        name: Logger name (default: "meeting_captioning")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   If None, uses Config.LOG_LEVEL
        log_file: Path to log file. If None, creates timestamped file in logs/
    
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logging("video_processor")
        >>> logger.info("Processing started")
    """
    # Ensure logs directory exists
    Config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Determine log level
    if log_level is None:
        log_level = Config.LOG_LEVEL
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt=Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    )
    
    console_formatter = logging.Formatter(
        fmt="%(levelname)-8s | %(name)s | %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Config.LOG_DIR / f"{name}_{timestamp}.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized: {name} at {log_level} level")
    logger.info(f"Log file: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    
    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("Method called")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)
