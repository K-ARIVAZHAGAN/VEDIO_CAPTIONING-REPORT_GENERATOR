"""
Audio extraction module for extracting audio from video files.

This module handles extraction of audio tracks from videos and
saves them in formats suitable for transcription.
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import wave

try:
    from imageio_ffmpeg import get_ffmpeg_exe
    FFMPEG_CMD = get_ffmpeg_exe()
except ImportError:
    FFMPEG_CMD = 'ffmpeg'  # Fallback to system ffmpeg

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import ProcessingError


class AudioExtractor(LoggerMixin):
    """
    Extracts audio from video files for transcription.
    
    Supports extraction to various audio formats:
    - WAV (best for transcription)
    - MP3 (compressed)
    - FLAC (lossless)
    
    Uses FFmpeg for reliable audio extraction.
    """
    
    def __init__(self):
        """Initialize the audio extractor."""
        self._check_ffmpeg()
        self.logger.info("Audio extractor initialized")
    
    def _check_ffmpeg(self) -> None:
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                [FFMPEG_CMD, '-version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.debug(f"FFmpeg is available: {FFMPEG_CMD}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise ProcessingError(
                "FFmpeg not found. Please install imageio-ffmpeg: pip install imageio-ffmpeg"
            )
    
    def extract_audio(
        self,
        video_path: Path,
        output_path: Optional[Path] = None,
        format: str = "wav",
        sample_rate: int = 16000,
        channels: int = 1
    ) -> Path:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (auto-generated if None)
            format: Output format (wav, mp3, flac)
            sample_rate: Audio sample rate in Hz (16000 recommended for transcription)
            channels: Number of audio channels (1=mono, 2=stereo)
            
        Returns:
            Path to extracted audio file
            
        Raises:
            ProcessingError: If audio extraction fails
            
        Example:
            >>> extractor = AudioExtractor()
            >>> audio_path = extractor.extract_audio("video.mp4")
        """
        self.logger.info(f"Extracting audio from: {video_path}")
        
        # Generate output path if not provided
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_audio.{format}"
        
        try:
            # Build FFmpeg command with AV1 codec support
            command = [
                FFMPEG_CMD,
                '-err_detect', 'ignore_err',     # Ignore codec errors
                '-i', str(video_path),           # Input file
                '-vn',                            # No video
                '-acodec', self._get_codec(format),
                '-ar', str(sample_rate),          # Sample rate
                '-ac', str(channels),             # Channels
                '-y',                             # Overwrite output
                str(output_path)
            ]
            
            # Add format-specific options
            if format == 'mp3':
                command.insert(-1, '-b:a')
                command.insert(-1, '192k')  # Bitrate for MP3
            
            self.logger.debug(f"FFmpeg command: {' '.join(command)}")
            
            # Run FFmpeg
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify output file exists
            if not output_path.exists():
                raise ProcessingError(f"Audio file not created: {output_path}")
            
            # Get audio info
            audio_info = self.get_audio_info(output_path)
            
            self.logger.info(
                f"Audio extracted successfully: {output_path} "
                f"({audio_info['duration']:.2f}s, {audio_info['sample_rate']}Hz)"
            )
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise ProcessingError(f"FFmpeg audio extraction failed: {error_msg}", e)
        except Exception as e:
            raise ProcessingError(f"Audio extraction failed", e)
    
    def _get_codec(self, format: str) -> str:
        """
        Get appropriate codec for audio format.
        
        Args:
            format: Audio format (wav, mp3, flac)
            
        Returns:
            FFmpeg codec name
        """
        codecs = {
            'wav': 'pcm_s16le',
            'mp3': 'libmp3lame',
            'flac': 'flac',
            'm4a': 'aac'
        }
        return codecs.get(format.lower(), 'pcm_s16le')
    
    def get_audio_info(self, audio_path: Path) -> Dict[str, Any]:
        """
        Get information about an audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing audio metadata
            
        Raises:
            ProcessingError: If audio info cannot be retrieved
        """
        try:
            # Use FFprobe to get audio info
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(audio_path)
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            import json
            data = json.loads(result.stdout)
            
            # Extract audio stream info
            audio_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            if not audio_stream:
                raise ProcessingError("No audio stream found")
            
            # Extract format info
            format_info = data.get('format', {})
            
            info = {
                'codec': audio_stream.get('codec_name'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': audio_stream.get('channels', 0),
                'duration': float(format_info.get('duration', 0)),
                'bit_rate': int(format_info.get('bit_rate', 0)),
                'size_bytes': int(format_info.get('size', 0)),
                'format': format_info.get('format_name')
            }
            
            return info
            
        except subprocess.CalledProcessError as e:
            raise ProcessingError(f"FFprobe failed: {e.stderr}", e)
        except Exception as e:
            raise ProcessingError(f"Failed to get audio info", e)
    
    def extract_audio_segment(
        self,
        video_path: Path,
        start_time: float,
        duration: float,
        output_path: Optional[Path] = None,
        format: str = "wav"
    ) -> Path:
        """
        Extract a segment of audio from video.
        
        Useful for processing long videos in chunks.
        
        Args:
            video_path: Path to input video file
            start_time: Start time in seconds
            duration: Duration in seconds
            output_path: Path for output audio file
            format: Output format
            
        Returns:
            Path to extracted audio segment
        """
        self.logger.info(
            f"Extracting audio segment: {start_time}s to {start_time + duration}s"
        )
        
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_segment_{start_time:.0f}.{format}"
        
        try:
            command = [
                FFMPEG_CMD,
                '-i', str(video_path),
                '-ss', str(start_time),
                '-t', str(duration),
                '-vn',
                '-acodec', self._get_codec(format),
                '-ar', '16000',
                '-ac', '1',
                '-y',
                str(output_path)
            ]
            
            subprocess.run(command, capture_output=True, text=True, check=True)
            
            self.logger.info(f"Audio segment extracted: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise ProcessingError(f"Audio segment extraction failed: {e.stderr}", e)
    
    def normalize_audio(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        target_level: float = -20.0
    ) -> Path:
        """
        Normalize audio levels for better transcription.
        
        Args:
            audio_path: Path to input audio file
            output_path: Path for output audio file
            target_level: Target loudness in dB LUFS
            
        Returns:
            Path to normalized audio file
        """
        self.logger.info(f"Normalizing audio: {audio_path}")
        
        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_normalized{audio_path.suffix}"
        
        try:
            # Two-pass normalization using FFmpeg loudnorm filter
            # First pass: analyze
            command_analyze = [
                FFMPEG_CMD,
                '-i', str(audio_path),
                '-af', f'loudnorm=I={target_level}:print_format=json',
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                command_analyze,
                capture_output=True,
                text=True
            )
            
            # Second pass: apply normalization
            command_normalize = [
                FFMPEG_CMD,
                '-i', str(audio_path),
                '-af', f'loudnorm=I={target_level}',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                str(output_path)
            ]
            
            subprocess.run(
                command_normalize,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"Audio normalized: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Audio normalization failed, using original: {e}")
            return audio_path
    
    def split_audio_by_silence(
        self,
        audio_path: Path,
        min_silence_duration: float = 1.0,
        silence_threshold: int = -40
    ) -> list[tuple[float, float]]:
        """
        Detect silent sections in audio for smart segmentation.
        
        Args:
            audio_path: Path to audio file
            min_silence_duration: Minimum silence duration in seconds
            silence_threshold: Silence threshold in dB
            
        Returns:
            List of (start, end) tuples for non-silent segments
        """
        self.logger.info(f"Detecting silence in: {audio_path}")
        
        try:
            command = [
                FFMPEG_CMD,
                '-i', str(audio_path),
                '-af', f'silencedetect=n={silence_threshold}dB:d={min_silence_duration}',
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            # Parse silence detection output
            import re
            silence_starts = []
            silence_ends = []
            
            for line in result.stderr.split('\n'):
                if 'silence_start' in line:
                    match = re.search(r'silence_start: ([\d.]+)', line)
                    if match:
                        silence_starts.append(float(match.group(1)))
                elif 'silence_end' in line:
                    match = re.search(r'silence_end: ([\d.]+)', line)
                    if match:
                        silence_ends.append(float(match.group(1)))
            
            # Create non-silent segments
            segments = []
            audio_info = self.get_audio_info(audio_path)
            duration = audio_info['duration']
            
            if not silence_starts:
                # No silence detected, return entire audio
                return [(0.0, duration)]
            
            # First segment
            if silence_starts[0] > 0:
                segments.append((0.0, silence_starts[0]))
            
            # Middle segments
            for i in range(len(silence_ends) - 1):
                segments.append((silence_ends[i], silence_starts[i + 1]))
            
            # Last segment
            if silence_ends and silence_ends[-1] < duration:
                segments.append((silence_ends[-1], duration))
            
            self.logger.info(f"Detected {len(segments)} non-silent segments")
            return segments
            
        except Exception as e:
            self.logger.warning(f"Silence detection failed: {e}")
            # Return entire audio as single segment
            info = self.get_audio_info(audio_path)
            return [(0.0, info['duration'])]
