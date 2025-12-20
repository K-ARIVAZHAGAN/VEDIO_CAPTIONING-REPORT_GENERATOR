# 🎬 Video Captioning & Report Generator

> **Automated video analysis with AI-powered transcription, scene detection, and comprehensive reporting**

**Zero Dependencies** | **Clone & Run** | **No Build Tools Required**

---

## ⚡ Quick Start (3 Commands)

### Windows
```powershell
git clone https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR.git
cd VEDIO_CAPTIONING-REPORT_GENERATOR
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### macOS / Linux
```bash
git clone https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR.git
cd VEDIO_CAPTIONING-REPORT_GENERATOR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Access at:** `http://localhost:5000`

---

## 🎯 What It Does

✅ **Video Input:** Local files, YouTube, Google Drive, Dropbox  
✅ **Scene Detection:** Automatically extracts key frames  
✅ **Transcription:** Speech-to-text with timestamps (Whisper AI)  
✅ **AI Summary:** Intelligent key points extraction (Local LLM)  
✅ **Captioned Video:** Burned-in captions on original video  
✅ **Reports:** PDF, DOCX, JSON, TXT formats  

---

## 📋 Features

### Input Sources
- **Local Files:** MP4, MOV, AVI, WebM, MKV
- **YouTube:** Any public video URL
- **Google Drive:** Direct shareable links
- **Dropbox:** Direct download links
- **Any URL:** Direct video file URLs

### Processing
- **Scene Detection:** Automatic scene change detection
- **Frame Extraction:** Key frames at transitions
- **Audio Transcription:** Whisper AI (offline, no API needed)
- **Caption Generation:** SRT format with timing
- **AI Analysis:** Local LLM for summaries (no cloud API)

### Outputs
- **Captioned Video:** Original with burned captions
- **Transcripts:** Full text with timestamps
- **Reports:** Professional PDF/DOCX/JSON/TXT
- **Scene Frames:** Individual JPG images
- **AI Summary:** Key points with timestamps

---

## 🌐 Cloud Video Setup

### Google Drive

**1. Get Shareable Link:**
```
Right-click file → Share → Copy link
Example: https://drive.google.com/file/d/1ABC...XYZ/view?usp=sharing
```

**2. Convert to Direct Download:**
```
Original: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
Direct:   https://drive.google.com/uc?export=download&id=FILE_ID
```

**3. Use in Application:**
- Paste the direct download link
- Or use original link (app converts automatically)

**Tip:** For large files (>100MB), you need to:
1. Make file public (Anyone with link can view)
2. Use the direct download format above

---

### Dropbox

**1. Get Shareable Link:**
```
Right-click file → Share → Copy link
Example: https://www.dropbox.com/s/abc123xyz/video.mp4?dl=0
```

**2. Convert to Direct Download:**
```
Original: https://www.dropbox.com/s/abc123xyz/video.mp4?dl=0
Direct:   https://www.dropbox.com/s/abc123xyz/video.mp4?dl=1
                                                         ↑
                                                    Change 0 to 1
```

**3. Use in Application:**
- Paste the link with `?dl=1` at the end
- Or use original (app converts automatically)

---

### YouTube

**Just paste the URL directly:**
```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
```

**Supported:**
- Standard videos
- Shorts (converted automatically)
- Unlisted videos (with link)

**Not Supported:**
- Private videos
- Age-restricted videos
- Region-locked videos

---

### OneDrive

**1. Get Shareable Link:**
```
Right-click file → Share → Copy link
Example: https://1drv.ms/v/s!ABC...XYZ
```

**2. Convert to Direct Download:**
```
Original: https://1drv.ms/v/s!ABC...XYZ
Direct:   https://api.onedrive.com/v1.0/shares/s!ABC...XYZ/root/content
```

Or use this simpler format:
```
Replace: https://1drv.ms/v/s!ABC123XYZ
With:    https://1drv.ms/v/s!ABC123XYZ?download=1
```

---

## 💾 Installation Details

### Requirements
- **Python 3.8+** (ONLY requirement!)
- **8GB RAM minimum** (16GB recommended for large videos)
- **Internet:** First-time download of models (~3GB)

### What Gets Installed
✅ **FFmpeg** - Bundled in imageio-ffmpeg (31MB)  
✅ **Whisper AI** - Speech recognition model  
✅ **Llama 3.2 3B** - Local LLM for summaries  
✅ **OpenCV** - Video processing  
✅ **PyTorch** - ML framework  

**Total install size:** ~3-4GB (mostly AI models)

### Windows Note
If `pip install -r requirements.txt` fails with "llama-cpp-python build error":
```powershell
# Install with pre-built wheel (no compiler needed)
pip install llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
pip install -r requirements.txt
```

---

## 🚀 Usage

### 1. Start Application
```bash
python app.py
```

### 2. Access Web Interface
```
http://localhost:5000
```

### 3. Upload/Paste Video
- **Local:** Drag & drop file
- **URL:** Paste YouTube/Drive/Dropbox link

### 4. Process
Click "Process Video" - automatically:
- Detects scenes
- Extracts audio
- Transcribes speech
- Generates captions
- Creates summary
- Exports reports

### 5. Download Results
- **Captioned Video:** MP4 with burned captions
- **Reports:** PDF, DOCX, JSON, TXT
- **Captions:** SRT subtitle file
- **Frames:** Individual scene images

---

## 📂 Project Structure

```
VEDIO_CAPTIONING-REPORT_GENERATOR/
├── app.py                      # Main entry point
├── install_windows.ps1         # Windows auto-installer
├── requirements.txt            # Python dependencies
├── meeting_captioning/         # Core package
│   ├── main_app.py            # Processing pipeline
│   ├── config.py              # Configuration
│   ├── processing/            # Video/audio processing
│   │   ├── scene_detector.py
│   │   ├── audio_extractor.py
│   │   └── caption_generator.py
│   ├── transcription/         # Speech-to-text
│   │   ├── transcriber.py
│   │   └── segmenter.py
│   ├── ai/                    # Local LLM integration
│   │   └── llm_processor.py
│   ├── reporting/             # Report generation
│   │   ├── report_builder.py
│   │   ├── pdf_exporter.py
│   │   └── docx_exporter.py
│   ├── io/                    # File I/O, video loading
│   │   ├── video_loader.py
│   │   └── file_manager.py
│   └── web/                   # Flask web interface
│       ├── flask_app.py
│       ├── static/            # CSS, JS
│       └── templates/         # HTML
├── models/                     # AI models (auto-downloaded)
├── outputs/                    # Processing results
└── logs/                       # Application logs
```

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create `.env` file:
```env
# OpenAI API (optional - for cloud transcription)
OPENAI_API_KEY=your_key_here

# Custom model path
LLAMA_MODEL_PATH=./models/llama-3.2-3b-instruct.Q4_K_M.gguf

# Server settings
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Processing settings
SCENE_THRESHOLD=30.0
MIN_SCENE_DURATION=1.0
WHISPER_MODEL=base
```

### Model Download

First run automatically downloads:
```
models/
└── llama-3.2-3b-instruct.Q4_K_M.gguf  (~2GB)
```

Manual download:
```bash
mkdir models
# Download from HuggingFace or llama.cpp releases
# Place in models/ folder
```

---

## 🔧 Management

### View Logs
```bash
# Real-time logs
tail -f logs/meeting_captioning_*.log

# All logs
cat logs/meeting_captioning_*.log
```

### Stop Application
```bash
# Ctrl+C in terminal
# Or find and kill process:
pkill -f "python app.py"    # Linux/Mac
taskkill /F /IM python.exe  # Windows
```

### Update Application
```bash
git pull
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --upgrade
python app.py
```

### Clear Old Sessions
```bash
# Remove old processing results
rm -rf outputs/session_*
```

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

### "llama-cpp-python build failed"
```bash
# Use pre-built wheel (Windows)
pip install llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### "FFmpeg not found"
```bash
# Should not happen - ffmpeg is bundled
# Verify:
python -c "from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())"
```

### "Port 5000 already in use"
```bash
# Change port in .env or:
FLASK_PORT=5001 python app.py
```

### Video download fails (Google Drive)
- File must be public (Anyone with link)
- Large files (>100MB) need direct download format
- Check file isn't deleted or moved

### Out of memory
- Reduce video resolution before processing
- Close other applications
- Use smaller Whisper model: `WHISPER_MODEL=tiny`

---

## 📊 Performance

### Processing Times (approximate)
- **10 min video:** ~5-10 minutes
- **30 min video:** ~15-25 minutes
- **1 hour video:** ~30-50 minutes

### Factors:
- CPU speed (faster = better)
- Video resolution (higher = slower)
- Scene complexity (more scenes = slower)
- Whisper model size (base is default)

### Optimization Tips:
1. Use `tiny` or `small` Whisper model for faster transcription
2. Reduce video resolution before upload
3. Close other applications to free RAM
4. Use SSD for faster I/O

---

## 🔐 Privacy

✅ **100% Local Processing** - No cloud APIs required  
✅ **No Data Upload** - Everything runs on your machine  
✅ **No Telemetry** - No tracking or analytics  
✅ **Open Source** - Full code transparency  

**Optional Cloud:** YouTube download, Google Drive/Dropbox fetching (only fetches video, doesn't upload data)

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

## 🙋 Support

**Issues:** Create issue on GitHub  
**Questions:** Check logs in `logs/` directory  
**Updates:** `git pull` to get latest version

---

## ✨ Tips

1. **Large Videos:** Split into smaller chunks for faster processing
2. **Cloud Storage:** Use direct download links for best reliability
3. **AI Features:** First run downloads models (~2GB) - be patient
4. **Reports:** PDF works best for sharing, JSON for programmatic access
5. **Captions:** SRT file works with VLC, YouTube, and most players

---

**Ready to Go!** Clone, install, and start processing videos. No setup hassle, no system dependencies, just Python.
