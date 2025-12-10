"""
Video processor module for coordinating video processing operations.

This module orchestrates the entire video processing pipeline.
"""

import cv2
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import ProcessingError
from meeting_captioning.processing.scene_detector import SceneDetector, Scene
from meeting_captioning.processing.audio_extractor import AudioExtractor


@dataclass
class VideoMetadata:
    """Video metadata container."""
    path: Path
    duration: float
    fps: float
    width: int
    height: int
    frame_count: int
    has_audio: bool
    size_bytes: int


class VideoProcessor(LoggerMixin):
    """
    Coordinates all video processing operations.
    
    Orchestrates scene detection, frame extraction, and audio processing.
    """
    
    def __init__(self):
        """Initialize the video processor."""
        self.scene_detector = SceneDetector()
        self.audio_extractor = AudioExtractor()
        self.logger.info("Video processor initialized")
    
    def get_video_metadata(self, video_path: Path) -> VideoMetadata:
        """Extract video metadata."""
        self.logger.info(f"Extracting metadata from: {video_path}")
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise ProcessingError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Check for audio
            has_audio = self._check_audio(video_path)
            
            metadata = VideoMetadata(
                path=video_path,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                frame_count=frame_count,
                has_audio=has_audio,
                size_bytes=video_path.stat().st_size
            )
            
            self.logger.info(
                f"Video metadata: {duration:.1f}s, {width}x{height}, "
                f"{fps} fps, audio={'yes' if has_audio else 'no'}"
            )
            
            return metadata
            
        except Exception as e:
            raise ProcessingError(f"Failed to extract metadata", e)
    
    def _check_audio(self, video_path: Path) -> bool:
        """Check if video has audio track."""
        try:
            audio_info = self.audio_extractor.get_audio_info(video_path)
            has_audio = audio_info['channels'] > 0
            self.logger.debug(f"Audio check for {video_path.name}: channels={audio_info.get('channels', 0)}, has_audio={has_audio}")
            return has_audio
        except Exception as e:
            self.logger.warning(f"Failed to check audio for {video_path.name}: {e}")
            # Assume video has audio if we can't check (fail-safe)
            return True
    
    def process_video(
        self,
        video_path: Path,
        extract_audio: bool = True,
        detect_scenes: bool = True,
        frame_callback: Optional[callable] = None,
        audio_output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Process video: extract audio, detect scenes, extract frames.
        
        Args:
            video_path: Path to video file
            extract_audio: Whether to extract audio
            detect_scenes: Whether to detect scene changes
            frame_callback: Callback for saving frames
            
        Returns:
            Dictionary with processing results
        """
        self.logger.info(f"Processing video: {video_path}")
        
        results = {
            'metadata': self.get_video_metadata(video_path),
            'audio_path': None,
            'scenes': [],
            'success': False
        }
        
        try:
            # Extract audio
            if extract_audio:
                if not results['metadata'].has_audio:
                    self.logger.warning(f"Video has no audio track: {video_path}")
                else:
                    self.logger.info(f"Extracting audio to: {audio_output_path}")
                    audio_path = self.audio_extractor.extract_audio(
                        video_path,
                        output_path=audio_output_path
                    )
                    results['audio_path'] = audio_path
                    self.logger.info(f"Audio extracted successfully: {audio_path}")
            else:
                self.logger.info("Audio extraction skipped (extract_audio=False)")
            
            # Detect scenes
            if detect_scenes:
                scenes = self.scene_detector.detect_scenes(
                    video_path,
                    save_frames=True,
                    frame_output_callback=frame_callback
                )
                results['scenes'] = scenes
                self.logger.info(f"Detected {len(scenes)} scenes")
            
            results['success'] = True
            self.logger.info("Video processing complete")
            return results
            
        except Exception as e:
            results['error'] = str(e)
            raise ProcessingError(f"Video processing failed", e)
