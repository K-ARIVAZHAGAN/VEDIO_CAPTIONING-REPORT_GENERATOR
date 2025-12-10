"""Cloud video downloader - Download videos from Google Drive and Dropbox."""

import os
import re
from pathlib import Path
from typing import Optional
import requests

from meeting_captioning.utils.logging_config import LoggerMixin


class CloudVideoDownloader(LoggerMixin):
    """Download videos from cloud storage services."""
    
    def __init__(self, download_dir: Optional[Path] = None):
        """
        Initialize cloud video downloader.
        
        Args:
            download_dir: Directory to save downloaded videos
        """
        from meeting_captioning.config import Config
        self.download_dir = download_dir or (Config.TEMP_DIR / 'downloads')
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_from_url(self, url: str) -> Optional[Path]:
        """
        Download video from cloud URL (auto-detects Google Drive or Dropbox).
        
        Args:
            url: Cloud storage URL
            
        Returns:
            Path to downloaded video file
        """
        if 'drive.google.com' in url or 'docs.google.com' in url:
            return self.download_from_google_drive(url)
        elif 'dropbox.com' in url:
            return self.download_from_dropbox(url)
        else:
            return self.download_direct_link(url)
    
    def download_from_google_drive(self, url: str) -> Optional[Path]:
        """
        Download video from Google Drive share link.
        
        Supports:
        - https://drive.google.com/file/d/FILE_ID/view
        - https://drive.google.com/open?id=FILE_ID
        
        Args:
            url: Google Drive share URL
            
        Returns:
            Path to downloaded file
        """
        try:
            # Extract file ID from URL
            file_id = None
            
            # Pattern 1: /file/d/FILE_ID/view
            match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
            if match:
                file_id = match.group(1)
            
            # Pattern 2: ?id=FILE_ID
            match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
            if match:
                file_id = match.group(1)
            
            if not file_id:
                self.logger.error(f"Could not extract Google Drive file ID from URL: {url}")
                return None
            
            self.logger.info(f"Downloading from Google Drive: {file_id}")
            
            # Use direct download URL
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            # Start download
            session = requests.Session()
            response = session.get(download_url, stream=True)
            
            # Handle large file confirmation
            if 'download_warning' in response.text or response.status_code != 200:
                # Try alternate method for large files
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
                response = session.get(download_url, stream=True)
            
            # Get filename from Content-Disposition header
            filename = self._get_filename_from_response(response, f"gdrive_{file_id}.mp4")
            output_path = self.download_dir / filename
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            self._download_with_progress(response, output_path, total_size)
            
            self.logger.info(f"Downloaded: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to download from Google Drive: {e}")
            return None
    
    def download_from_dropbox(self, url: str) -> Optional[Path]:
        """
        Download video from Dropbox share link.
        
        Supports:
        - https://www.dropbox.com/s/FILE_ID/filename.mp4?dl=0
        - https://www.dropbox.com/scl/fi/FILE_ID/filename.mp4?dl=0
        
        Args:
            url: Dropbox share URL
            
        Returns:
            Path to downloaded file
        """
        try:
            # Convert to direct download link
            if '?dl=0' in url:
                download_url = url.replace('?dl=0', '?dl=1')
            elif '?dl=1' not in url:
                download_url = url + '?dl=1'
            else:
                download_url = url
            
            # Also handle www.dropbox.com -> dl.dropboxusercontent.com
            download_url = download_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
            
            self.logger.info(f"Downloading from Dropbox: {download_url}")
            
            # Start download
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Get filename
            filename = self._get_filename_from_response(response, "dropbox_video.mp4")
            output_path = self.download_dir / filename
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            self._download_with_progress(response, output_path, total_size)
            
            self.logger.info(f"Downloaded: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to download from Dropbox: {e}")
            return None
    
    def download_direct_link(self, url: str) -> Optional[Path]:
        """
        Download video from direct HTTP/HTTPS link.
        
        Args:
            url: Direct video URL
            
        Returns:
            Path to downloaded file
        """
        try:
            self.logger.info(f"Downloading from URL: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get filename
            filename = self._get_filename_from_response(response, "video.mp4")
            output_path = self.download_dir / filename
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            self._download_with_progress(response, output_path, total_size)
            
            self.logger.info(f"Downloaded: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to download from URL: {e}")
            return None
    
    def _get_filename_from_response(self, response, default: str) -> str:
        """Extract filename from Content-Disposition header."""
        content_disposition = response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            filename = re.findall('filename="?([^"]+)"?', content_disposition)
            if filename:
                return filename[0]
        
        # Try to get from URL
        url_filename = response.url.split('/')[-1].split('?')[0]
        if url_filename and '.' in url_filename:
            return url_filename
        
        return default
    
    def _download_with_progress(self, response, output_path: Path, total_size: int):
        """Download file with progress logging."""
        chunk_size = 8192
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (chunk_size * 100) == 0:  # Log every 100 chunks
                            self.logger.info(f"Download progress: {percent:.1f}%")
