"""
Video loader module for handling multiple video sources.

This module provides a unified interface for loading videos from:
- Local file system
- Web URLs (including authenticated/private videos)
- YouTube URLs
- Cloud storage platforms (Google Drive, Dropbox, etc.)
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    raise ImportError("yt-dlp is required. Install with: pip install yt-dlp")

try:
    from imageio_ffmpeg import get_ffmpeg_exe
    FFMPEG_PATH = get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = 'ffmpeg'  # Fallback to system ffmpeg

from meeting_captioning.config import Config
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import VideoLoadError


class VideoLoader(LoggerMixin):
    """
    Unified video loader supporting multiple sources.
    
    Supports:
    - Local files: MP4, MOV, AVI, MKV, FLV, WMV
    - YouTube URLs
    - Direct video URLs
    - Google Drive links
    - Dropbox links
    - Other web platform videos
    
    Attributes:
        temp_dir: Directory for temporary downloads
    """
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize the video loader.
        
        Args:
            temp_dir: Directory for temporary files (uses Config.TEMP_DIR if None)
        """
        self.temp_dir = temp_dir or Config.TEMP_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests Session
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def load_video(self, source: str) -> Path:
        """
        Load video from any supported source.
        
        This is the main entry point that determines the source type
        and delegates to the appropriate loader.
        
        Args:
            source: Video source (local path or URL)
            
        Returns:
            Path to the loaded video file (local)
            
        Raises:
            VideoLoadError: If video cannot be loaded
            
        Example:
            >>> loader = VideoLoader()
            >>> video_path = loader.load_video("/path/to/video.mp4")
            >>> video_path = loader.load_video("https://youtube.com/watch?v=...")
        """
        self.logger.info(f"Loading video from source: {source}")
        
        try:
            # Check if it's a local file
            if self._is_local_file(source):
                return self._load_local_file(source)
            
            # Check if it's a URL
            elif self._is_url(source):
                # Determine URL type
                if self._is_youtube_url(source):
                    return self._load_youtube_video(source)
                elif self._is_google_drive_url(source):
                    return self._load_google_drive_video(source)
                elif self._is_dropbox_url(source):
                    return self._load_dropbox_video(source)
                else:
                    return self._load_web_video(source)
            
            else:
                raise VideoLoadError(f"Unrecognized video source format: {source}")
        
        except VideoLoadError:
            raise
        except Exception as e:
            raise VideoLoadError(f"Failed to load video from {source}", e)
    
    def _is_local_file(self, source: str) -> bool:
        """Check if source is a local file path."""
        path = Path(source)
        return path.exists() and path.is_file()
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube URL."""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
            r'(https?://)?(www\.)?youtube\.com/watch\?v=',
            r'(https?://)?(www\.)?youtu\.be/',
        ]
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def _is_google_drive_url(self, url: str) -> bool:
        """Check if URL is a Google Drive URL."""
        return 'drive.google.com' in url
    
    def _is_dropbox_url(self, url: str) -> bool:
        """Check if URL is a Dropbox URL."""
        return 'dropbox.com' in url
    
    def _load_local_file(self, file_path: str) -> Path:
        """
        Load a local video file.
        
        Args:
            file_path: Path to local video file
            
        Returns:
            Path object to the video file
            
        Raises:
            VideoLoadError: If file doesn't exist or has unsupported format
        """
        path = Path(file_path)
        
        if not path.exists():
            raise VideoLoadError(f"Video file not found: {file_path}")
        
        if path.suffix.lower() not in Config.SUPPORTED_VIDEO_FORMATS:
            raise VideoLoadError(
                f"Unsupported video format: {path.suffix}. "
                f"Supported formats: {', '.join(Config.SUPPORTED_VIDEO_FORMATS)}"
            )
        
        self.logger.info(f"Loaded local video: {path}")
        return path
    
    def _load_youtube_video(self, url: str) -> Path:
        """
        Download a YouTube video.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Path to downloaded video file
            
        Raises:
            VideoLoadError: If download fails
        """
        self.logger.info(f"Downloading YouTube video: {url}")
        
        # Use yt-dlp for downloading (supports YouTube, Google Drive, Dropbox, and more)
        if not YTDLP_AVAILABLE:
            raise VideoLoadError("yt-dlp is required. Install with: pip install yt-dlp")
        
        return self._download_with_ytdlp(url)
    
    def _download_with_ytdlp(self, url: str) -> Path:
        """Download video using yt-dlp (supports YouTube, Google Drive, Dropbox, and more)."""
        try:
            output_template = str(self.temp_dir / '%(title)s_%(id)s.%(ext)s')
            
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'nocheckcertificate': True,
                'prefer_insecure': False,
                'cookiefile': None,
                'extract_flat': False,
                'ffmpeg_location': FFMPEG_PATH,  # Use bundled ffmpeg
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.info(f"Extracting video info from: {url}")
                info = ydl.extract_info(url, download=True)
                
                # Get the actual filename
                if 'requested_downloads' in info and info['requested_downloads']:
                    filepath = info['requested_downloads'][0]['filepath']
                else:
                    # Construct filename from info
                    title = info.get('title', 'video').replace('/', '_').replace('\\', '_')
                    video_id = info.get('id', 'unknown')
                    ext = info.get('ext', 'mp4')
                    filepath = str(self.temp_dir / f"{title}_{video_id}.{ext}")
            
            downloaded_file = Path(filepath)
            
            if not downloaded_file.exists():
                # Try to find the file with similar name
                pattern = f"*{info.get('id', '')}*.mp4"
                matches = list(self.temp_dir.glob(pattern))
                if matches:
                    downloaded_file = matches[0]
                else:
                    raise VideoLoadError(f"Downloaded file not found: {downloaded_file}")
            
            self.logger.info(f"Video downloaded: {downloaded_file}")
            return downloaded_file
            
        except Exception as e:
            raise VideoLoadError(f"Failed to download video with yt-dlp: {str(e)}", e)
    
    def _load_google_drive_video(self, url: str) -> Path:
        """
        Download video from Google Drive.
        
        Args:
            url: Google Drive share URL
            
        Returns:
            Path to downloaded video file
        """
        self.logger.info(f"Downloading from Google Drive: {url}")
        
        try:
            # Extract file ID from URL
            file_id = self._extract_google_drive_id(url)
            
            # Use yt-dlp for Google Drive (more reliable)
            if YTDLP_AVAILABLE:
                gdrive_url = f"https://drive.google.com/file/d/{file_id}/view"
                return self._download_with_ytdlp(gdrive_url)
            
            # Fallback to direct download
            session = requests.Session()
            
            # First request to get confirmation token for large files
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            response = session.get(download_url, stream=True)
            
            # Check for large file warning
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={value}"
                    break
            
            # Download the file
            output_path = self.temp_dir / f"gdrive_{file_id}.mp4"
            response = session.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info(f"Google Drive video downloaded: {output_path}")
            return output_path
            
        except Exception as e:
            raise VideoLoadError(f"Failed to download from Google Drive", e)
    
    def _extract_google_drive_id(self, url: str) -> str:
        """Extract file ID from Google Drive URL."""
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/open\?id=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise VideoLoadError("Could not extract Google Drive file ID from URL")
    
    def _load_dropbox_video(self, url: str) -> Path:
        """
        Download video from Dropbox.
        
        Args:
            url: Dropbox share URL
            
        Returns:
            Path to downloaded video file
        """
        self.logger.info(f"Downloading from Dropbox: {url}")
        
        try:
            # Use yt-dlp for Dropbox (more reliable)
            if YTDLP_AVAILABLE:
                return self._download_with_ytdlp(url)
            
            # Fallback: Convert share URL to direct download URL
            if '?dl=0' in url:
                download_url = url.replace('?dl=0', '?dl=1')
            elif '?dl=1' not in url:
                download_url = url + ('&' if '?' in url else '?') + 'dl=1'
            else:
                download_url = url
            
            # Extract filename
            filename = "dropbox_video.mp4"
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            if path_parts:
                potential_filename = path_parts[-1]
                if '.' in potential_filename:
                    filename = potential_filename
            
            return self._download_file(download_url, filename=filename)
            
        except Exception as e:
            raise VideoLoadError(f"Failed to download from Dropbox", e)
    
    def _load_web_video(self, url: str) -> Path:
        """
        Download video from generic web URL.
        
        Args:
            url: Direct video URL
            
        Returns:
            Path to downloaded video file
        """
        self.logger.info(f"Downloading from web: {url}")
        
        try:
            # Extract filename from URL or use default
            parsed = urlparse(url)
            filename = Path(parsed.path).name or "web_video.mp4"
            
            return self._download_file(url, filename=filename)
            
        except Exception as e:
            raise VideoLoadError(f"Failed to download web video", e)
    
    def _download_file(
        self,
        url: str,
        filename: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Path:
        """
        Download a file from URL with progress tracking.
        
        Args:
            url: Download URL
            filename: Output filename
            headers: Optional HTTP headers
            
        Returns:
            Path to downloaded file
        """
        output_path = self.temp_dir / filename
        
        try:
            response = self._session.get(
                url,
                headers=headers,
                stream=True,
                timeout=Config.DOWNLOAD_TIMEOUT
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as f:
                if total_size:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=Config.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = (downloaded / total_size) * 100
                            self.logger.debug(f"Download progress: {percent:.1f}%")
                else:
                    f.write(response.content)
            
            self.logger.info(f"Downloaded file: {output_path}")
            return output_path
            
        except requests.exceptions.Timeout:
            raise VideoLoadError(f"Download timeout after {Config.DOWNLOAD_TIMEOUT}s")
        except requests.exceptions.RequestException as e:
            raise VideoLoadError(f"Download failed", e)
    
    def validate_video(self, video_path: Path) -> Dict[str, Any]:
        """
        Validate video file and extract basic metadata.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata (duration, size, format)
            
        Raises:
            VideoLoadError: If video is invalid
        """
        import cv2
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise VideoLoadError(f"Cannot open video file: {video_path}")
            
            # Extract metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            # Check duration limit
            if duration > Config.MAX_VIDEO_DURATION:
                self.logger.warning(
                    f"Video duration ({duration:.1f}s) exceeds recommended limit "
                    f"({Config.MAX_VIDEO_DURATION}s)"
                )
            
            metadata = {
                'path': str(video_path),
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'size_bytes': video_path.stat().st_size,
                'format': video_path.suffix
            }
            
            self.logger.info(f"Video validated: {duration:.1f}s, {width}x{height}, {fps} fps")
            return metadata
            
        except Exception as e:
            raise VideoLoadError(f"Video validation failed", e)
    
    def cleanup_temp_files(self) -> None:
        """Remove all temporary downloaded files."""
        try:
            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    self.logger.debug(f"Removed temp file: {file}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp files: {e}")
