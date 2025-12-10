# Meeting Video Captioning System

Automated video captioning and documentation generator with scene detection and transcription.

## Features

- Multi-source video support (local, YouTube, Google Drive, Dropbox)
- Automatic transcription with Whisper
- Scene detection and frame extraction
- Caption burning with FFmpeg
- JSON reports with browser-based PDF/DOCX/TXT export

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure (edit config.py)
# Set your API keys and preferences

# Run web app
python app.py
```

Visit `http://localhost:5000`

## Requirements

- Python 3.8+
- FFmpeg installed
- 4GB+ RAM recommended

## Configuration

Edit `config.py`:
- Whisper model size
- Scene detection thresholds
- Caption styling
- Output paths
