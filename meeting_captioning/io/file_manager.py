"""
File manager module for organizing output files.

This module handles the organization and management of all output files
including videos, reports, logs, and temporary files.
"""

import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import MeetingCaptioningError


class FileManager(LoggerMixin):
    """
    Manages output files and directory structure.
    
    Creates organized output directories with timestamps and manages
    all file operations for the application.
    
    Attributes:
        session_dir: Directory for current session outputs
        video_dir: Directory for video outputs
        report_dir: Directory for report outputs
        frames_dir: Directory for extracted frames
    """
    
    def __init__(self, session_name: Optional[str] = None):
        """
        Initialize the file manager.
        
        Args:
            session_name: Name for the processing session (auto-generated if None)
        """
        if session_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"session_{timestamp}"
        
        # Create session directory
        self.session_dir = Config.get_output_subdir(session_name)
        
        # Create subdirectories
        self.video_dir = self.session_dir / "videos"
        self.report_dir = self.session_dir / "reports"
        self.frames_dir = self.session_dir / "frames"
        self.captions_dir = self.session_dir / "captions"
        self.audio_dir = self.session_dir / "audio"
        
        self._create_directories()
        
        self.logger.info(f"File manager initialized for session: {session_name}")
        self.logger.info(f"Output directory: {self.session_dir}")
    
    def _create_directories(self) -> None:
        """Create all necessary subdirectories."""
        for directory in [self.video_dir, self.report_dir, self.frames_dir, self.captions_dir, self.audio_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
    
    def get_video_output_path(self, filename: str) -> Path:
        """
        Get path for video output file.
        
        Args:
            filename: Output filename (without path)
            
        Returns:
            Full path for the video output
        """
        return self.video_dir / filename
    
    def get_report_output_path(self, filename: str, format: str = "pdf") -> Path:
        """
        Get path for report output file.
        
        Args:
            filename: Output filename (without extension)
            format: Report format (pdf, docx, txt)
            
        Returns:
            Full path for the report output
        """
        return self.report_dir / f"{filename}.{format}"
    
    def get_frame_output_path(self, frame_number: int, timestamp: float) -> Path:
        """
        Get path for extracted frame.
        
        Args:
            frame_number: Frame sequence number
            timestamp: Timestamp in seconds
            
        Returns:
            Full path for the frame image
        """
        filename = f"frame_{frame_number:06d}_t{timestamp:.2f}.jpg"
        return self.frames_dir / filename
    
    def get_caption_file_path(self, format: str = "srt") -> Path:
        """
        Get path for caption file.
        
        Args:
            format: Caption format (srt, vtt, ass)
            
        Returns:
            Full path for the caption file
        """
        return self.captions_dir / f"captions.{format}"
    
    def get_audio_output_path(self, filename: str = "audio.wav") -> Path:
        """
        Get path for audio output file.
        
        Args:
            filename: Output filename (with extension)
            
        Returns:
            Full path for the audio output
        """
        return self.audio_dir / filename
    
    def get_transcript_output_path(self, filename: str = "transcript.txt") -> Path:
        """
        Get path for transcript output file.
        
        Args:
            filename: Output filename (with extension)
            
        Returns:
            Full path for the transcript output
        """
        return self.audio_dir / filename
    
    def save_video(self, source_path: Path, output_filename: str) -> Path:
        """
        Copy video to output directory.
        
        Args:
            source_path: Source video file path
            output_filename: Desired output filename
            
        Returns:
            Path to saved video
        """
        output_path = self.get_video_output_path(output_filename)
        
        try:
            shutil.copy2(source_path, output_path)
            self.logger.info(f"Saved video: {output_path}")
            return output_path
        except Exception as e:
            raise MeetingCaptioningError(f"Failed to save video", e)
    
    def save_frame(self, frame_data: Any, frame_number: int, timestamp: float) -> Path:
        """
        Save extracted frame as image.
        
        Args:
            frame_data: Frame data (numpy array)
            frame_number: Frame sequence number
            timestamp: Timestamp in seconds
            
        Returns:
            Path to saved frame
        """
        import cv2
        
        output_path = self.get_frame_output_path(frame_number, timestamp)
        
        try:
            cv2.imwrite(str(output_path), frame_data)
            self.logger.debug(f"Saved frame: {output_path}")
            return output_path
        except Exception as e:
            raise MeetingCaptioningError(f"Failed to save frame", e)
    
    def list_frames(self) -> List[Path]:
        """
        List all saved frames.
        
        Returns:
            List of frame file paths
        """
        frames = sorted(self.frames_dir.glob("frame_*.jpg"))
        return frames
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of session outputs.
        
        Returns:
            Dictionary containing file counts and sizes
        """
        def get_dir_size(directory: Path) -> int:
            """Calculate total size of files in directory."""
            return sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
        
        def count_files(directory: Path, pattern: str = "*") -> int:
            """Count files in directory matching pattern."""
            return len(list(directory.glob(pattern)))
        
        summary = {
            'session_dir': str(self.session_dir),
            'total_size_bytes': get_dir_size(self.session_dir),
            'videos': {
                'count': count_files(self.video_dir),
                'size_bytes': get_dir_size(self.video_dir)
            },
            'reports': {
                'count': count_files(self.report_dir),
                'size_bytes': get_dir_size(self.report_dir),
                'pdf_count': count_files(self.report_dir, "*.pdf"),
                'docx_count': count_files(self.report_dir, "*.docx"),
                'txt_count': count_files(self.report_dir, "*.txt")
            },
            'frames': {
                'count': count_files(self.frames_dir, "*.jpg"),
                'size_bytes': get_dir_size(self.frames_dir)
            },
            'captions': {
                'count': count_files(self.captions_dir),
                'size_bytes': get_dir_size(self.captions_dir)
            }
        }
        
        return summary
    
    def create_manifest(self) -> Path:
        """
        Create a manifest file listing all outputs.
        
        Returns:
            Path to manifest file
        """
        manifest_path = self.session_dir / "manifest.txt"
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(f"Meeting Video Captioning - Session Manifest\n")
                f.write(f"=" * 60 + "\n\n")
                f.write(f"Session: {self.session_dir.name}\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # List videos
                f.write("Videos:\n")
                for video in self.video_dir.glob("*"):
                    if video.is_file():
                        size_mb = video.stat().st_size / (1024 * 1024)
                        f.write(f"  - {video.name} ({size_mb:.2f} MB)\n")
                f.write("\n")
                
                # List reports
                f.write("Reports:\n")
                for report in self.report_dir.glob("*"):
                    if report.is_file():
                        size_kb = report.stat().st_size / 1024
                        f.write(f"  - {report.name} ({size_kb:.2f} KB)\n")
                f.write("\n")
                
                # Frame count
                frame_count = len(list(self.frames_dir.glob("*.jpg")))
                f.write(f"Frames: {frame_count} extracted\n\n")
                
                # Summary
                summary = self.get_session_summary()
                total_size_mb = summary['total_size_bytes'] / (1024 * 1024)
                f.write(f"Total Size: {total_size_mb:.2f} MB\n")
            
            self.logger.info(f"Created manifest: {manifest_path}")
            return manifest_path
            
        except Exception as e:
            raise MeetingCaptioningError(f"Failed to create manifest", e)
    
    def cleanup_frames(self) -> None:
        """Delete all extracted frames to save space."""
        try:
            for frame in self.frames_dir.glob("*.jpg"):
                frame.unlink()
            self.logger.info("Cleaned up frame files")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup frames: {e}")
    
    def cleanup_session(self) -> None:
        """Delete entire session directory."""
        try:
            shutil.rmtree(self.session_dir)
            self.logger.info(f"Deleted session directory: {self.session_dir}")
        except Exception as e:
            raise MeetingCaptioningError(f"Failed to cleanup session", e)
    
    def open_output_directory(self) -> None:
        """Open the output directory in file explorer."""
        import platform
        import subprocess
        
        try:
            system = platform.system()
            
            if system == "Windows":
                subprocess.Popen(['explorer', str(self.session_dir)])
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', str(self.session_dir)])
            else:  # Linux
                subprocess.Popen(['xdg-open', str(self.session_dir)])
            
            self.logger.info(f"Opened output directory: {self.session_dir}")
            
        except Exception as e:
            self.logger.warning(f"Failed to open output directory: {e}")
    
    def get_latest_video(self) -> Optional[Path]:
        """
        Get the most recently created video file.
        
        Returns:
            Path to latest video, or None if no videos exist
        """
        videos = list(self.video_dir.glob("*"))
        if not videos:
            return None
        
        latest = max(videos, key=lambda p: p.stat().st_mtime)
        return latest
    
    def get_all_reports(self) -> Dict[str, List[Path]]:
        """
        Get all generated reports grouped by format.
        
        Returns:
            Dictionary mapping format to list of report paths
        """
        reports = {
            'pdf': list(self.report_dir.glob("*.pdf")),
            'docx': list(self.report_dir.glob("*.docx")),
            'txt': list(self.report_dir.glob("*.txt"))
        }
        return reports
