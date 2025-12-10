"""
Meeting Video Captioning - Flask Web Application Entry Point
Run this file to start the web server
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meeting_captioning.web.flask_app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("🎬 Meeting Video Captioning - Web Application")
    print("="*60)
    print("\n🚀 Starting Flask server...")
    print("📡 Server URL: http://localhost:5000")
    print("📡 Or access from network: http://<your-ip>:5000")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',  # Allow external access
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=False  # Disable auto-reload to preserve job status
    )
