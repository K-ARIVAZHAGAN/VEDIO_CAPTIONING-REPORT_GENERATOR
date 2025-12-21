"""
Flask Web Application for Meeting Video Captioning
"""
import os
import json
import uuid
from pathlib import Path
from threading import Thread, Lock
from typing import Dict, Optional
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from meeting_captioning.config import Config
from meeting_captioning.main_app import MeetingCaptioningApp
from meeting_captioning.utils.logging_config import setup_logging

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Cloud storage configuration (optional - for frontend only if needed)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
DROPBOX_APP_KEY = os.getenv('DROPBOX_APP_KEY', '')


# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max file size
app.config['UPLOAD_FOLDER'] = Config.OUTPUT_DIR / 'uploads'
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Setup logging
setup_logging()

# Global state for tracking processing jobs
processing_jobs: Dict[str, Dict] = {}
jobs_lock = Lock()


ALLOWED_EXTENSIONS = {
    'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4v', 'mpg', 'mpeg'
}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_job_status(job_id: str) -> Optional[Dict]:
    """Get status of a processing job"""
    with jobs_lock:
        return processing_jobs.get(job_id)


def update_job_status(job_id: str, status: str, progress: float = 0.0, 
                      message: str = "", result: Optional[Dict] = None):
    """Update status of a processing job"""
    with jobs_lock:
        if job_id not in processing_jobs:
            processing_jobs[job_id] = {
                'job_id': job_id,
                'created_at': datetime.now().isoformat()
            }
        
        processing_jobs[job_id].update({
            'status': status,
            'progress': progress,
            'message': message,
            'updated_at': datetime.now().isoformat()
        })
        
        if result:
            processing_jobs[job_id]['result'] = result


def process_video_task(job_id: str, video_path: str, 
                       model_size: str, session_name: Optional[str]):
    """Background task to process video"""
    try:
        update_job_status(job_id, 'processing', 0.0, 'Initializing...')
        
        # Progress callback
        def progress_callback(progress: float, message: str):
            update_job_status(job_id, 'processing', progress, message)
        
        # Initialize the main app
        captioning_app = MeetingCaptioningApp(
            session_name=session_name
        )
        
        # Process the video with progress callback (only JSON report generated)
        result = captioning_app.process_video(
            video_source=video_path,
            progress_callback=progress_callback
        )
        
        if result.success:
            # Load report to get actual metadata
            import json
            from datetime import datetime
            report_data = {}
            processing_time = 0
            try:
                json_report = result.session_dir / 'reports' / 'report.json'
                if json_report.exists():
                    with open(json_report, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    # Calculate processing time from session name and report date
                    try:
                        # Session name format: session_20251209_224626_20251209_224626
                        session_name_parts = session_name.split('_')
                        if len(session_name_parts) >= 3:
                            start_date = session_name_parts[1]  # 20251209
                            start_time = session_name_parts[2]  # 224626
                            start_str = f"{start_date} {start_time}"
                            start_dt = datetime.strptime(start_str, "%Y%m%d %H%M%S")
                            
                            # Report date from JSON
                            report_date_str = report_data.get('date', '')
                            if report_date_str:
                                end_dt = datetime.fromisoformat(report_date_str)
                                processing_time = round((end_dt - start_dt).total_seconds(), 1)
                    except Exception:
                        pass
            except Exception:
                pass
            
            # Build result data with actual values
            result_data = {
                'session_dir': str(result.session_dir),
                'video_output': str(result.captioned_video_path) if result.captioned_video_path else None,
                'caption_file': str(result.session_dir / 'captions' / 'captions.srt') if result.captioned_video_path else None,
                'report_files': [str(p) for p in result.report_paths.values()],
                'transcript_file': str(result.session_dir / 'audio' / 'transcript.txt'),
                'scenes_count': len(report_data.get('scenes', [])),
                'duration': report_data.get('metadata', {}).get('duration', 0),
                'processing_time': processing_time
            }
            
            update_job_status(job_id, 'completed', 100.0, 
                            'Processing completed successfully!', result_data)
        else:
            update_job_status(job_id, 'failed', 0.0, 
                            f'Processing failed: {result.error}')
    
    except Exception as e:
        update_job_status(job_id, 'failed', 0.0, f'Error: {str(e)}')


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html',
                         google_client_id=GOOGLE_CLIENT_ID,
                         google_api_key=GOOGLE_API_KEY,
                         dropbox_app_key=DROPBOX_APP_KEY)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a video file.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = app.config['UPLOAD_FOLDER'] / unique_filename
        
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'filepath': str(filepath),
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process', methods=['POST'])
def process_video():
    """Start video processing"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Get parameters
        video_source = data.get('video_source')
        is_url = data.get('is_url', False)
        model_size = data.get('model_size', 'base')
        session_name = data.get('session_name')
        
        if not video_source:
            return jsonify({'error': 'No video source provided'}), 400
        
        # If URL, check if it's a cloud storage link and download first
        if is_url:
            from meeting_captioning.cloud.cloud_downloader import CloudVideoDownloader
            
            # Check if it's YouTube URL
            if any(domain in video_source.lower() for domain in ['youtube.com', 'youtu.be']):
                try:
                    import yt_dlp
                    
                    # Configure yt-dlp
                    download_folder = app.config['UPLOAD_FOLDER']
                    ydl_opts = {
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'outtmpl': str(download_folder / '%(title)s.%(ext)s'),
                        'merge_output_format': 'mp4',
                        'quiet': True,
                        'no_warnings': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_source, download=True)
                        downloaded_file = ydl.prepare_filename(info)
                        
                        if not downloaded_file or not Path(downloaded_file).exists():
                            return jsonify({'error': 'Failed to download YouTube video'}), 400
                        
                        video_source = downloaded_file
                        is_url = False  # Now it's a local file
                        
                except Exception as e:
                    return jsonify({'error': f'YouTube download failed: {str(e)}'}), 400
            
            # Check if it's a cloud storage URL
            elif any(domain in video_source.lower() for domain in ['drive.google.com', 'dropbox.com', 'dropboxusercontent.com', 'docs.google.com']):
                try:
                    downloader = CloudVideoDownloader()
                    downloaded_path = downloader.download_from_url(video_source)
                    
                    if not downloaded_path:
                        return jsonify({'error': 'Failed to download video from cloud storage'}), 400
                    
                    video_source = str(downloaded_path)
                    is_url = False  # Now it's a local file
                    
                except Exception as e:
                    return jsonify({'error': f'Cloud download failed: {str(e)}'}), 400
        
        # Validate file exists if not URL
        if not is_url and not Path(video_source).exists():
            return jsonify({'error': 'Video file not found'}), 404
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start background processing (only JSON report generated)
        thread = Thread(
            target=process_video_task,
            args=(job_id, video_source, model_size, session_name)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def job_status(job_id: str):
    """Get job status"""
    status = get_job_status(job_id)
    
    if not status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(status)


@app.route('/api/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id: str):
    """Cancel a processing job"""
    with jobs_lock:
        if job_id in processing_jobs:
            processing_jobs[job_id]['status'] = 'cancelled'
            processing_jobs[job_id]['message'] = 'Processing cancelled by user'
            app.logger.info(f"Job {job_id} cancelled by user")
            return jsonify({'success': True, 'message': 'Job cancelled'})
        else:
            return jsonify({'error': 'Job not found'}), 404


@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Handle AI chat questions about the video"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        report_path = data.get('report_path', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not report_path:
            return jsonify({'error': 'Report path is required'}), 400
        
        # Initialize LLM
        from meeting_captioning.ai.llm_processor import LLMProcessor
        llm = LLMProcessor()
        
        if not llm.is_available():
            return jsonify({
                'error': 'AI features not available',
                'message': 'Phi-2 model not loaded. Run: python download_model.py'
            }), 503
        
        # Load report
        report_file = Path(report_path)
        if not report_file.exists():
            return jsonify({'error': 'Report not found'}), 404
        
        llm.load_report(report_file)
        
        # Get answer
        answer = llm.answer_question(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        })
        
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename: str):
    """Download a generated file"""
    try:
        # Handle absolute paths (Mac/Linux start with /, Windows with C:\)
        if filename.startswith('/') or (len(filename) > 1 and filename[1] == ':'):
            filepath = Path(filename)
        else:
            filepath = Path('/') / filename if not os.name == 'nt' else Path(filename)
        
        # Log the request for debugging
        app.logger.info(f"Download request for: {filepath}")
        
        if not filepath.exists():
            app.logger.error(f"File not found: {filepath}")
            
            # Try to find the file with a sanitized name in the same directory
            parent_dir = filepath.parent
            file_stem = filepath.stem
            file_ext = filepath.suffix
            
            if parent_dir.exists():
                # List all files in the directory for debugging
                app.logger.info(f"Files in {parent_dir}:")
                for f in parent_dir.iterdir():
                    app.logger.info(f"  - {f.name}")
                
                # Try to find a match (case-insensitive, sanitized)
                for potential_file in parent_dir.glob(f"*{file_ext}"):
                    if potential_file.stem.lower().replace('_', '').replace('-', '') == file_stem.lower().replace('_', '').replace('-', ''):
                        app.logger.info(f"Found potential match: {potential_file}")
                        filepath = potential_file
                        break
            
            if not filepath.exists():
                return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Check if requesting as attachment or inline (for video/captions)
        as_attachment = request.args.get('attachment', 'true').lower() == 'true'
        
        app.logger.info(f"Serving file: {filepath} (attachment={as_attachment})")
        
        return send_file(
            str(filepath),
            as_attachment=as_attachment,
            download_name=filepath.name
        )
    
    except Exception as e:
        app.logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcript/<path:filename>', methods=['GET'])
def get_transcript(filename: str):
    """Get transcript content as text"""
    try:
        # Handle absolute paths (Mac/Linux start with /, Windows with C:\)
        if filename.startswith('/') or (len(filename) > 1 and filename[1] == ':'):
            filepath = Path(filename)
        else:
            filepath = Path('/') / filename if not os.name == 'nt' else Path(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Read and return text content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/captions/<path:filename>', methods=['GET'])
def get_captions(filename: str):
    """Get caption/SRT content"""
    try:
        # Handle absolute paths (Mac/Linux start with /, Windows with C:\)
        if filename.startswith('/') or (len(filename) > 1 and filename[1] == ':'):
            filepath = Path(filename)
        else:
            filepath = Path('/') / filename if not os.name == 'nt' else Path(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Read and return SRT content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': 'text/vtt; charset=utf-8'}
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all processing jobs"""
    with jobs_lock:
        return jsonify({
            'jobs': list(processing_jobs.values())
        })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


def create_app():
    """Factory function to create Flask app"""
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
