"""
Configuration management module for the Meeting Video Captioning application.

This module handles all configuration settings including paths, processing parameters,
and application settings. It supports loading from environment variables and provides
sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Central configuration class for the application.
    
    Attributes:
        PROJECT_ROOT: Root directory of the project
        OUTPUT_DIR: Directory for generated outputs
        LOG_DIR: Directory for application logs
        TEMP_DIR: Directory for temporary files
        MAX_VIDEO_DURATION: Maximum video duration in seconds (2 hours)
        SUPPORTED_VIDEO_FORMATS: List of supported video file extensions
        DEFAULT_LANGUAGE: Default language for transcription
        FRAME_DIFF_THRESHOLD: Threshold for scene change detection (0-100)
        SCENE_MIN_DURATION: Minimum duration between scenes in seconds
        CAPTION_FONT_SIZE: Font size for burned-in captions
        CAPTION_FONT_COLOR: Font color for captions (RGB)
        CAPTION_BG_COLOR: Background color for captions (RGBA)
        CHUNK_SIZE: Audio chunk size for streaming downloads
    """
    
    # Base paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    
    # Allow custom directories via environment variables
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", str(PROJECT_ROOT / "outputs")))
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(PROJECT_ROOT / "logs")))
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", str(PROJECT_ROOT / "temp")))
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"
    
    # Video processing settings
    MAX_VIDEO_DURATION: int = 7200  # 2 hours in seconds
    SUPPORTED_VIDEO_FORMATS: tuple = ('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv')
    
    # Transcription settings
    DEFAULT_LANGUAGE: str = os.getenv("TRANSCRIPTION_LANGUAGE", "en")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
    
    # Scene detection settings
    FRAME_DIFF_THRESHOLD: float = float(os.getenv("FRAME_DIFF_THRESHOLD", "30.0"))
    SCENE_MIN_DURATION: float = float(os.getenv("SCENE_MIN_DURATION", "1.0"))
    
    # Caption settings
    CAPTION_FONT_SIZE: int = int(os.getenv("CAPTION_FONT_SIZE", "24"))
    CAPTION_FONT_COLOR: str = os.getenv("CAPTION_FONT_COLOR", "white")
    CAPTION_BG_COLOR: str = os.getenv("CAPTION_BG_COLOR", "black@0.5")
    CAPTION_MAX_CHARS: int = int(os.getenv("CAPTION_MAX_CHARS", "60"))
    
    # Download settings
    CHUNK_SIZE: int = 8192
    DOWNLOAD_TIMEOUT: int = int(os.getenv("DOWNLOAD_TIMEOUT", "300"))  # 5 minutes
    
    # YouTube settings
    YOUTUBE_QUALITY: str = os.getenv("YOUTUBE_QUALITY", "highest")
    
    # Credentials (for private video access)
    WEB_VIDEO_USERNAME: Optional[str] = os.getenv("WEB_VIDEO_USERNAME")
    WEB_VIDEO_PASSWORD: Optional[str] = os.getenv("WEB_VIDEO_PASSWORD")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Report settings
    REPORT_TITLE_FONT_SIZE: int = 16
    REPORT_BODY_FONT_SIZE: int = 11
    REPORT_INCLUDE_SCREENSHOTS: bool = True
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [cls.OUTPUT_DIR, cls.LOG_DIR, cls.TEMP_DIR, cls.ASSETS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_output_subdir(cls, session_name: str) -> Path:
        """
        Create and return a timestamped output subdirectory for a session.
        
        Args:
            session_name: Name identifier for the processing session
            
        Returns:
            Path to the session output directory
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subdir = cls.OUTPUT_DIR / f"{session_name}_{timestamp}"
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary containing all configuration settings
        """
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def update_from_dict(cls, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration updates
        """
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)


# Ensure directories exist on module import
Config.ensure_directories()
