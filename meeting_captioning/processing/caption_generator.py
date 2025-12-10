"""
Caption generator module for burning captions into videos.

This module generates SRT caption files and burns them into videos.
CRITICAL Windows FFmpeg fixes applied to avoid path parsing errors.
"""

import os
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.time_utils import format_timestamp
from meeting_captioning.utils.error_handling import ProcessingError


@dataclass
class Caption:
    """Represents a single caption/subtitle."""
    index: int
    start_time: float
    end_time: float
    text: str


class CaptionGenerator(LoggerMixin):
    """
    Generates caption files and burns them into videos.
    
    Supports:
    - SRT (SubRip) format
    - VTT (WebVTT) format
    - Burning captions into video using FFmpeg
    
    Windows-safe implementation that avoids FFmpeg path parsing issues by:
    1. Using temp directory with simple ASCII filename for SRT
    2. Running FFmpeg with cwd set to temp directory
    3. Passing only filename in subtitles filter (no absolute paths)
    4. Sanitizing output filenames to remove emojis/special chars
    """
    
    def __init__(self):
        """Initialize caption generator."""
        self.logger.info("Caption generator initialized")
    
    def create_srt_file(
        self,
        captions: List[Caption],
        output_path: Path
    ) -> Path:
        """
        Create SRT caption file.
        
        Args:
            captions: List of Caption objects
            output_path: Path for output SRT file
            
        Returns:
            Path to created SRT file
        """
        self.logger.info(f"Creating SRT file: {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for caption in captions:
                    # Write caption index
                    f.write(f"{caption.index}\n")
                    
                    # Write timestamps
                    start = format_timestamp(caption.start_time, include_ms=True, format_type="srt")
                    end = format_timestamp(caption.end_time, include_ms=True, format_type="srt")
                    f.write(f"{start} --> {end}\n")
                    
                    # Write caption text
                    f.write(f"{caption.text}\n\n")
            
            self.logger.info(f"SRT file created with {len(captions)} captions")
            return output_path
            
        except Exception as e:
            raise ProcessingError(f"Failed to create SRT file", e)
    
    def burn_captions(
        self,
        video_path: Path,
        srt_path: Path,
        output_path: Path,
        font_size: Optional[int] = None,
        font_color: Optional[str] = None,
        bg_color: Optional[str] = None
    ) -> Path:
        """
        Burn captions into video using FFmpeg.
        
        CRITICAL WINDOWS FIX:
        - Copies SRT to temp directory with simple ASCII name "temp_captions.srt"
        - Runs FFmpeg with cwd=temp_dir
        - Uses only filename in subtitles filter: subtitles=filename=temp_captions.srt:charenc=UTF-8
        - This completely avoids Windows path parsing issues (C:, backslashes, emojis)
        
        Args:
            video_path: Input video file (can have emojis/special chars)
            srt_path: SRT caption file
            output_path: Output video file (will be sanitized)
            font_size: Caption font size
            font_color: Caption font color
            bg_color: Caption background color
            
        Returns:
            Path to captioned video (sanitized filename)
        """
        self.logger.info(f"Burning captions into video: {video_path}")
        
        font_size = font_size or Config.CAPTION_FONT_SIZE
        font_color = font_color or Config.CAPTION_FONT_COLOR
        bg_color = bg_color or Config.CAPTION_BG_COLOR
        
        temp_dir = None
        try:
            # ====================================================================
            # STEP 1: Create temp directory and copy SRT with simple ASCII name
            # ====================================================================
            temp_dir = Path(tempfile.mkdtemp(prefix="caption_srt_"))
            temp_srt = temp_dir / "temp_captions.srt"
            shutil.copy2(srt_path, temp_srt)
            
            self.logger.debug(f"Temp SRT created: {temp_srt}")
            
            # ====================================================================
            # STEP 2: Sanitize output filename (NOT input video path)
            # ====================================================================
            output_name_clean = self._sanitize_filename(output_path.name)
            output_path_clean = output_path.parent / output_name_clean
            
            self.logger.info(f"Original output name: {output_path.name}")
            self.logger.info(f"Sanitized output name: {output_name_clean}")
            
            # ====================================================================
            # STEP 3: Build FFmpeg command
            # CRITICAL: Use only filename in subtitles filter, NOT full path
            # ====================================================================
            
            # Build subtitles filter - ONLY filename, no path
            subtitles_filter = f"subtitles=filename=temp_captions.srt:charenc=UTF-8"
            
            # Use .as_posix() for cross-platform compatibility
            # FFmpeg handles forward slashes on Windows fine for file I/O
            command = [
                "ffmpeg",
                "-i", video_path.as_posix(),          # Input can have any chars
                "-vf", subtitles_filter,              # Filter uses simple filename only
                "-c:v", "libx264",                    # H.264 codec
                "-preset", "ultrafast",               # Fast encoding
                "-crf", "23",                         # Quality (18-28 range)
                "-c:a", "copy",                       # Copy audio without re-encoding
                "-y",                                 # Overwrite output
                output_path_clean.as_posix()          # Output with sanitized name
            ]
            
            self.logger.info("=" * 70)
            self.logger.info("FFmpeg Command:")
            self.logger.info(f"  CWD: {temp_dir}")
            self.logger.info(f"  Input: {video_path}")
            self.logger.info(f"  Filter: {subtitles_filter}")
            self.logger.info(f"  Output: {output_path_clean}")
            self.logger.info(f"  Full command: {' '.join(command)}")
            self.logger.info("=" * 70)
            
            # ====================================================================
            # STEP 4: Run FFmpeg with cwd=temp_dir
            # CRITICAL: FFmpeg will look for temp_captions.srt in its cwd
            # ====================================================================
            result = subprocess.run(
                command,
                cwd=str(temp_dir),                    # CRITICAL: Set cwd to temp dir
                capture_output=True,
                text=True,
                check=True
            )
            
            # Log FFmpeg output for debugging
            if result.stdout:
                self.logger.debug(f"FFmpeg stdout: {result.stdout[:500]}")
            if result.stderr:
                self.logger.debug(f"FFmpeg stderr: {result.stderr[:500]}")
            
            self.logger.info(f"✓ Captioned video created: {output_path_clean}")
            
            return output_path_clean
            
        except subprocess.CalledProcessError as e:
            # Log detailed error information
            error_msg = f"Caption burning failed with exit code {e.returncode}"
            self.logger.error("=" * 70)
            self.logger.error(error_msg)
            self.logger.error(f"Command: {e.cmd}")
            if e.stdout:
                self.logger.error(f"STDOUT:\n{e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR:\n{e.stderr}")
            self.logger.error("=" * 70)
            
            raise ProcessingError(f"Caption burning failed: {e.stderr}", e)
            
        except Exception as e:
            self.logger.error(f"Unexpected error during caption burning: {e}")
            raise ProcessingError(f"Caption burning failed: {str(e)}", e)
            
        finally:
            # ====================================================================
            # STEP 5: Clean up temp directory
            # ====================================================================
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    self.logger.debug(f"Temp directory cleaned up: {temp_dir}")
                except Exception as e:
                    # Non-fatal - just log the warning
                    self.logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove emojis and special characters.
        
        This ensures output filenames work on all filesystems and avoid
        issues with FFmpeg or other tools.
        
        Args:
            filename: Original filename (may contain emojis, unicode, special chars)
            
        Returns:
            Sanitized filename (ASCII alphanumeric, dots, dashes, underscores only)
        """
        # Extract extension
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            base_name, extension = name_parts
        else:
            base_name = filename
            extension = ""
        
        # Step 1: Remove all non-ASCII characters (includes emojis)
        base_name = re.sub(r'[^\x00-\x7F]+', '', base_name)
        
        # Step 2: Replace invalid chars with underscore (keep only alphanumeric, dot, dash, underscore)
        base_name = re.sub(r'[^\w.\-]', '_', base_name)
        
        # Step 3: Collapse multiple underscores/spaces into single underscore
        base_name = re.sub(r'[_\s]+', '_', base_name)
        
        # Step 4: Remove leading/trailing underscores
        base_name = base_name.strip('_')
        
        # Step 5: Ensure we have something left
        if not base_name:
            base_name = "captioned_video"
        
        # Reconstruct filename
        if extension:
            return f"{base_name}.{extension}"
        return base_name
    
    def _color_to_hex(self, color: str) -> str:
        """
        Convert color name to hex for FFmpeg.
        Handles formats like 'white', 'black@0.5' (with transparency).
        """
        # Extract base color and transparency if present
        if '@' in color:
            base_color = color.split('@')[0].strip()
        else:
            base_color = color.strip()
        
        colors = {
            'white': 'FFFFFF',
            'black': '000000',
            'yellow': 'FFFF00',
            'red': 'FF0000',
            'green': '00FF00',
            'blue': '0000FF'
        }
        return colors.get(base_color.lower(), 'FFFFFF')


# ============================================================================
# DIAGNOSTIC / SELF-TEST FUNCTION
# ============================================================================

def test_caption_burning():
    """
    Self-test function for caption burning.
    
    Tests the burn_captions function with a minimal example.
    Run this to verify FFmpeg integration works on your system.
    
    Usage:
        python -m meeting_captioning.processing.caption_generator
    """
    import sys
    from meeting_captioning.utils.logging_config import setup_logging
    
    setup_logging("caption_generator_test")
    
    print("=" * 70)
    print("Caption Burning Self-Test")
    print("=" * 70)
    
    # You need to provide test files for this to work
    print("\nTo run this test:")
    print("1. Place a short test video at: test_video.mp4")
    print("2. Create a test SRT file at: test_captions.srt")
    print("3. Run: python -m meeting_captioning.processing.caption_generator")
    print("\nTest SRT content example:")
    print("""1
00:00:00,000 --> 00:00:02,000
This is a test caption

2
00:00:02,000 --> 00:00:04,000
Testing emoji handling 🔥
""")
    
    test_video = Path("test_video.mp4")
    test_srt = Path("test_captions.srt")
    test_output = Path("test_output_captioned.mp4")
    
    if not test_video.exists():
        print(f"\n❌ Test video not found: {test_video}")
        print("Please provide a test video to run this diagnostic.")
        return False
    
    if not test_srt.exists():
        print(f"\n❌ Test SRT not found: {test_srt}")
        print("Please provide a test SRT file to run this diagnostic.")
        return False
    
    try:
        generator = CaptionGenerator()
        result_path = generator.burn_captions(
            video_path=test_video,
            srt_path=test_srt,
            output_path=test_output
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"Output video: {result_path}")
        print(f"File exists: {result_path.exists()}")
        print(f"File size: {result_path.stat().st_size / 1024 / 1024:.2} MB")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run self-test when module is executed directly."""
    import sys
    success = test_caption_burning()
    sys.exit(0 if success else 1)

