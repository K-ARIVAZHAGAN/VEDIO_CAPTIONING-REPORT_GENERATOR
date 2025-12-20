"""
Transcription module for converting speech to text.

This module uses OpenAI Whisper for high-quality speech-to-text transcription.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json

# Check FFmpeg availability for Whisper
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    FFMPEG_PATH = get_ffmpeg_exe()
    # Validate binary exists
    if not os.path.isfile(FFMPEG_PATH):
        raise FileNotFoundError(f"FFmpeg binary not found at {FFMPEG_PATH}")
    
    # CRITICAL: Whisper expects 'ffmpeg.exe' (or 'ffmpeg' on Linux/Mac)
    # Create a copy with the standard name if it doesn't exist
    ffmpeg_dir = os.path.dirname(FFMPEG_PATH)
    standard_name = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
    standard_path = os.path.join(ffmpeg_dir, standard_name)
    
    if not os.path.exists(standard_path):
        shutil.copy2(FFMPEG_PATH, standard_path)
    
    # Set environment variable for Whisper to find FFmpeg
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
    
except (ImportError, FileNotFoundError) as e:
    raise RuntimeError(
        "FFmpeg is not available!\n"
        "Whisper requires FFmpeg for audio processing.\n"
        "Please reinstall: pip install --force-reinstall imageio-ffmpeg\n"
        f"Error: {e}"
    )

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import TranscriptionError


@dataclass
class TranscriptionSegment:
    """Represents a segment of transcribed text."""
    id: int
    start: float
    end: float
    text: str
    confidence: float = 1.0
    
    @property
    def duration(self) -> float:
        """Get segment duration."""
        return self.end - self.start


class Transcriber(LoggerMixin):
    """
    Transcribes audio to text using Whisper.
    
    Supports multiple Whisper model sizes:
    - tiny: Fastest, least accurate
    - base: Good balance (default)
    - small: Better accuracy
    - medium: High accuracy
    - large: Best accuracy, slowest
    """
    
    def __init__(
        self,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
        device: str = "auto"
    ):
        """
        Initialize the transcriber.
        
        Args:
            model_size: Whisper model size (tiny/base/small/medium/large)
            language: Language code (e.g., 'en', 'es', 'fr')
            device: Device to use ('cpu', 'cuda', or 'auto')
        """
        # Ensure model_size and language are not None
        self.model_size = model_size if model_size is not None else (Config.WHISPER_MODEL if hasattr(Config, 'WHISPER_MODEL') and Config.WHISPER_MODEL else "base")
        self.language = language if language is not None else (Config.DEFAULT_LANGUAGE if hasattr(Config, 'DEFAULT_LANGUAGE') and Config.DEFAULT_LANGUAGE else "en")
        self.device = device if device else "auto"
        
        self.logger.info(
            f"Initializing transcriber: model={self.model_size}, "
            f"language={self.language}, device={self.device}"
        )
        
        self.model = self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            import whisper
            import torch
            
            # Determine device
            if self.device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = self.device
            
            self.logger.info(f"Loading Whisper {self.model_size} model on {device}...")
            
            # Load model - device parameter should be string or None, not NoneType check issue
            if device:
                model = whisper.load_model(self.model_size, device=device)
            else:
                model = whisper.load_model(self.model_size)
            
            self.logger.info("Whisper model loaded successfully")
            return model
            
        except ImportError:
            raise TranscriptionError(
                "Whisper not installed. Install with: pip install openai-whisper"
            )
        except Exception as e:
            raise TranscriptionError(f"Failed to load Whisper model", e)
    
    def transcribe(
        self,
        audio_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional Whisper options
            
        Returns:
            Dictionary with transcription results
            
        Raises:
            TranscriptionError: If transcription fails
        """
        self.logger.info(f"Transcribing audio: {audio_path}")
        
        # Runtime validation: Check FFmpeg still exists
        if not os.path.isfile(FFMPEG_PATH):
            raise TranscriptionError(
                f"FFmpeg binary not found at {FFMPEG_PATH}\n"
                "The FFmpeg binary may have been deleted.\n"
                "Whisper requires FFmpeg for audio processing.\n"
                "Please reinstall: pip install --force-reinstall imageio-ffmpeg"
            )
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=self.language if self.language and self.language != "auto" else None,
                verbose=False,
                **kwargs
            )
            
            self.logger.info(
                f"Transcription complete: {len(result['segments'])} segments, "
                f"{len(result['text'])} characters"
            )
            
            return result
            
        except Exception as e:
            raise TranscriptionError(f"Transcription failed", e)
    
    def transcribe_to_segments(
        self,
        audio_path: Path,
        **kwargs
    ) -> List[TranscriptionSegment]:
        """
        Transcribe audio and return structured segments.
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional Whisper options
            
        Returns:
            List of TranscriptionSegment objects
        """
        result = self.transcribe(audio_path, **kwargs)
        
        segments = []
        for i, seg in enumerate(result['segments']):
            segment = TranscriptionSegment(
                id=i + 1,
                start=seg['start'],
                end=seg['end'],
                text=seg['text'].strip(),
                confidence=seg.get('avg_logprob', 1.0)
            )
            segments.append(segment)
        
        return segments
    
    def transcribe_with_timestamps(
        self,
        audio_path: Path
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Transcribe with word-level timestamps.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (full_text, word_timestamps)
        """
        self.logger.info("Transcribing with word-level timestamps")
        
        result = self.transcribe(audio_path, word_timestamps=True)
        
        full_text = result['text']
        word_timestamps = []
        
        for segment in result['segments']:
            if 'words' in segment:
                word_timestamps.extend(segment['words'])
        
        return full_text, word_timestamps
    
    def save_transcription(
        self,
        result: Dict[str, Any],
        output_path: Path,
        format: str = "json"
    ) -> Path:
        """
        Save transcription to file.
        
        Args:
            result: Transcription result from Whisper
            output_path: Output file path
            format: Output format (json, txt, srt)
            
        Returns:
            Path to saved file
        """
        self.logger.info(f"Saving transcription to: {output_path}")
        
        try:
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            
            elif format == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
            
            elif format == "srt":
                self._save_as_srt(result, output_path)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Transcription saved: {output_path}")
            return output_path
            
        except Exception as e:
            raise TranscriptionError(f"Failed to save transcription", e)
    
    def _save_as_srt(self, result: Dict[str, Any], output_path: Path) -> None:
        """Save transcription as SRT subtitle file."""
        from meeting_captioning.utils.time_utils import format_timestamp
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], 1):
                start = format_timestamp(segment['start'], include_ms=True, format_type="srt")
                end = format_timestamp(segment['end'], include_ms=True, format_type="srt")
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
