"""
Scene detection module for identifying content changes in videos.

This module detects scene changes, slide transitions, UI interactions,
and other visual changes in meeting videos using computer vision techniques.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import ProcessingError


@dataclass
class Scene:
    """
    Represents a detected scene in the video.
    
    Attributes:
        scene_number: Sequential scene number
        start_time: Start time in seconds
        end_time: End time in seconds (None for last scene)
        start_frame: Starting frame number
        end_frame: Ending frame number (None for last scene)
        frame_path: Path to representative frame image
        change_score: Magnitude of change (0-100)
        description: Optional scene description
    """
    scene_number: int
    start_time: float
    end_time: Optional[float]
    start_frame: int
    end_frame: Optional[int]
    frame_path: Optional[Path]
    change_score: float
    description: str = ""
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate scene duration in seconds."""
        if self.end_time is not None:
            return self.end_time - self.start_time
        return None


class SceneDetector(LoggerMixin):
    """
    Detects scene changes and content transitions in videos.
    
    Uses multiple techniques:
    - Frame difference analysis
    - Histogram comparison
    - Edge detection for UI changes
    - Motion detection
    
    Attributes:
        threshold: Sensitivity threshold for scene detection (0-100)
        min_scene_duration: Minimum duration between scene changes
    """
    
    def __init__(
        self,
        threshold: Optional[float] = None,
        min_scene_duration: Optional[float] = None
    ):
        """
        Initialize the scene detector.
        
        Args:
            threshold: Detection threshold (uses Config.FRAME_DIFF_THRESHOLD if None)
            min_scene_duration: Minimum scene duration (uses Config.SCENE_MIN_DURATION if None)
        """
        self.threshold = threshold or Config.FRAME_DIFF_THRESHOLD
        self.min_scene_duration = min_scene_duration or Config.SCENE_MIN_DURATION
        
        self.logger.info(
            f"Scene detector initialized: threshold={self.threshold}, "
            f"min_duration={self.min_scene_duration}s"
        )
    
    def detect_scenes(
        self,
        video_path: Path,
        save_frames: bool = True,
        frame_output_callback: Optional[callable] = None
    ) -> List[Scene]:
        """
        Detect all scene changes in a video.
        
        Args:
            video_path: Path to video file
            save_frames: Whether to extract and save representative frames
            frame_output_callback: Callback function(frame_data, frame_num, timestamp) -> Path
            
        Returns:
            List of detected scenes
            
        Raises:
            ProcessingError: If scene detection fails
        """
        self.logger.info(f"Starting scene detection: {video_path}")
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise ProcessingError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            scenes: List[Scene] = []
            scene_number = 1
            prev_frame = None
            last_scene_time = 0.0
            
            frame_num = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_num / fps
                
                # Analyze frame if enough time has passed since last scene
                if current_time - last_scene_time >= self.min_scene_duration:
                    if prev_frame is not None:
                        # Calculate change score
                        change_score = self._calculate_frame_difference(prev_frame, frame)
                        
                        # Detect scene change
                        if change_score > self.threshold:
                            # Save frame if requested
                            frame_path = None
                            if save_frames and frame_output_callback:
                                frame_path = frame_output_callback(frame, frame_num, current_time)
                            
                            # Create scene object
                            scene = Scene(
                                scene_number=scene_number,
                                start_time=current_time,
                                end_time=None,
                                start_frame=frame_num,
                                end_frame=None,
                                frame_path=frame_path,
                                change_score=change_score
                            )
                            
                            # Update previous scene's end time
                            if scenes:
                                scenes[-1].end_time = current_time
                                scenes[-1].end_frame = frame_num
                            
                            scenes.append(scene)
                            scene_number += 1
                            last_scene_time = current_time
                            
                            self.logger.debug(
                                f"Scene {scene_number-1} detected at {current_time:.2f}s "
                                f"(score: {change_score:.2f})"
                            )
                
                prev_frame = frame.copy()
                frame_num += 1
                
                # Progress logging
                if frame_num % 300 == 0:  # Every ~10 seconds at 30fps
                    progress = (frame_num / total_frames) * 100
                    self.logger.info(f"Scene detection progress: {progress:.1f}%")
            
            cap.release()
            
            # Add final scene if we have any scenes
            if not scenes:
                # No scene changes detected - treat entire video as one scene
                scene = Scene(
                    scene_number=1,
                    start_time=0.0,
                    end_time=total_frames / fps,
                    start_frame=0,
                    end_frame=total_frames,
                    frame_path=None,
                    change_score=0.0,
                    description="No scene changes detected"
                )
                scenes.append(scene)
            else:
                # Update last scene's end time
                scenes[-1].end_time = total_frames / fps
                scenes[-1].end_frame = total_frames
            
            self.logger.info(f"Scene detection complete: {len(scenes)} scenes detected")
            return scenes
            
        except ProcessingError:
            raise
        except Exception as e:
            raise ProcessingError(f"Scene detection failed", e)
    
    def _calculate_frame_difference(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray
    ) -> float:
        """
        Calculate difference score between two frames.
        
        Uses multiple techniques:
        - Structural similarity (SSIM)
        - Histogram comparison
        - Mean squared error
        
        Args:
            frame1: First frame
            frame2: Second frame
            
        Returns:
            Difference score (0-100, higher = more different)
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Mean Squared Error
        mse = np.mean((gray1.astype(float) - gray2.astype(float)) ** 2)
        mse_score = min(100, (mse / 100))  # Normalize to 0-100
        
        # Method 2: Histogram comparison
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        hist_score = (1 - cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)) * 100
        
        # Method 3: Structural Similarity (approximate)
        # For speed, we use a simpler edge-based comparison
        edges1 = cv2.Canny(gray1, 50, 150)
        edges2 = cv2.Canny(gray2, 50, 150)
        edge_diff = np.sum(edges1 != edges2) / edges1.size * 100
        
        # Combine scores with weights
        combined_score = (mse_score * 0.3 + hist_score * 0.4 + edge_diff * 0.3)
        
        return combined_score
    
    def extract_keyframes(
        self,
        video_path: Path,
        num_keyframes: int = 10,
        frame_output_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract evenly-spaced keyframes from video.
        
        Useful for generating summary thumbnails.
        
        Args:
            video_path: Path to video file
            num_keyframes: Number of keyframes to extract
            frame_output_callback: Callback to save frames
            
        Returns:
            List of keyframe info dictionaries
        """
        self.logger.info(f"Extracting {num_keyframes} keyframes from {video_path}")
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise ProcessingError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            # Calculate frame intervals
            interval = total_frames // (num_keyframes + 1)
            
            keyframes = []
            
            for i in range(1, num_keyframes + 1):
                frame_num = i * interval
                timestamp = frame_num / fps
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                
                if ret:
                    frame_path = None
                    if frame_output_callback:
                        frame_path = frame_output_callback(frame, frame_num, timestamp)
                    
                    keyframes.append({
                        'frame_number': frame_num,
                        'timestamp': timestamp,
                        'frame_path': frame_path
                    })
            
            cap.release()
            
            self.logger.info(f"Extracted {len(keyframes)} keyframes")
            return keyframes
            
        except Exception as e:
            raise ProcessingError(f"Keyframe extraction failed", e)
    
    def detect_slide_transitions(
        self,
        video_path: Path,
        sensitivity: float = 0.8
    ) -> List[float]:
        """
        Detect slide transitions (common in presentation recordings).
        
        Uses high sensitivity to catch even subtle slide changes.
        
        Args:
            video_path: Path to video file
            sensitivity: Detection sensitivity (0-1, higher = more sensitive)
            
        Returns:
            List of timestamps where slides change
        """
        # Adjust threshold for slide detection
        adjusted_threshold = self.threshold * (1 - sensitivity)
        
        self.logger.info(f"Detecting slide transitions with sensitivity={sensitivity}")
        
        old_threshold = self.threshold
        self.threshold = adjusted_threshold
        
        try:
            scenes = self.detect_scenes(video_path, save_frames=False)
            transitions = [scene.start_time for scene in scenes if scene.scene_number > 1]
            
            self.logger.info(f"Detected {len(transitions)} slide transitions")
            return transitions
            
        finally:
            self.threshold = old_threshold
