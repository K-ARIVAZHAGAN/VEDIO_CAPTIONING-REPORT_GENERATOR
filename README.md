# 🎬 Meeting Video Captioning & Documentation System

> **Automated video analysis, captioning, and comprehensive report generation with AI-powered insights**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Objectives & Requirements](#-objectives--requirements)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Installation Guide](#-installation-guide)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Component Details](#-component-details)
- [Additional Features](#-additional-features-beyond-requirements)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Performance Notes](#-performance-notes)

---

## 🎯 Project Overview

The **Meeting Video Captioning & Documentation System** is an automated Python-based application that processes meeting videos and generates:
1. **Captioned Videos** - Original video with burned-in captions (visible on screen)
2. **Comprehensive Reports** - Detailed documentation with timestamps, transcripts, scenes, and summaries
3. **AI-Powered Insights** - Intelligent summaries and key point extraction using local LLM

### Project Goal

Ensure **no important information is missed** from meeting videos by automatically capturing:
- Every screen transition and scene change
- Every spoken word with precise timestamps
- Every interaction and content change
- Contextual summaries and key insights

---

## 📝 Objectives & Requirements

### ✅ Functional Requirements (ALL IMPLEMENTED)

#### 1. Video Input Support
- ✅ **Local Video Files**: MP4, MOV, AVI, WebM, MKV
- ✅ **YouTube Videos**: Public URLs with automatic download
- ✅ **Cloud Storage**: Google Drive, Dropbox direct links
- ✅ **Web Platform Videos**: Downloadable video URLs

#### 2. Video Processing
- ✅ **Scene Detection**: Extract frames on content changes (transitions, slides)
- ✅ **Frame Extraction**: Capture every screen and significant visual change
- ✅ **Caption Generation**: Synchronized captions with video segments
- ✅ **Speech-to-Text**: Audio transcription using OpenAI Whisper
- ✅ **Interaction Detection**: Document transitions and scene changes
- ✅ **Summarization**: Key points for each video segment

#### 3. Report Generation
- ✅ **Timestamps**: Precise timing for every screen and caption
- ✅ **Scene Descriptions**: Documented interactions and transitions
- ✅ **Segment Summaries**: Key points discussed in each section
- ✅ **Multiple Formats**: PDF, DOCX, TXT export options

#### 4. Single-Click Process
- ✅ **One-Click Execution**: Upload video → Process → Get results
- ✅ **Automated Pipeline**: Fully automated from input to output
- ✅ **Minimal User Input**: Simple web interface, no technical expertise required

### ✅ Non-Functional Requirements (ALL IMPLEMENTED)

#### Performance
- ✅ Efficient processing for videos up to 2+ hours
- ✅ Parallel processing where possible (scene detection, transcription)
- ✅ Progress tracking with real-time status updates

#### Cross-Platform Support
- ✅ Windows, macOS, Linux compatible
- ✅ Platform-independent file handling
- ✅ Universal path management

#### Usability
- ✅ Clean, intuitive web-based UI (Google Material Design)
- ✅ Drag-and-drop file upload
- ✅ Real-time progress tracking
- ✅ No configuration required for basic usage

#### Security
- ✅ Safe handling of sensitive video data
- ✅ Local processing (no data sent to external servers except Whisper API if configured)
- ✅ Secure session management
- ✅ Privacy-focused design

#### Error Handling
- ✅ Comprehensive error catching and logging
- ✅ User-friendly error messages
- ✅ Graceful degradation on failures
- ✅ Detailed logs for troubleshooting

#### Scalability & Reliability
- ✅ Handles videos up to 2+ hours without performance degradation
- ✅ Consistent output quality
- ✅ Robust error recovery
- ✅ Memory-efficient processing

---

## 🚀 Key Features

### Core Features (Per Requirements)

1. **🎥 Multi-Source Video Processing**
   - Local file upload with drag-and-drop
   - YouTube video download and processing
   - Cloud storage link support (Google Drive, Dropbox)
   - Format support: MP4, MOV, AVI, WebM, MKV

2. **🎬 Intelligent Scene Detection**
   - Automatic detection of scene changes
   - Frame extraction at transition points
   - Visual content change tracking
   - Thumbnail generation for each scene

3. **🎙️ High-Quality Transcription**
   - OpenAI Whisper integration (base/small/medium/large models)
   - Word-level timestamps
   - Multi-language support
   - Speaker separation (optional)

4. **📝 Comprehensive Captioning**
   - SRT caption file generation
   - Burned-in captions on video
   - Customizable styling (font, size, position, colors)
   - Synchronized timing with audio

5. **📊 Detailed Report Generation**
   - **Summary**: High-level video overview
   - **Timeline**: All captions with precise timestamps
   - **Scenes**: Visual transitions and frame captures
   - **Key Points**: Important moments and topics
   - **Full Transcript**: Complete word-for-word transcription
   - **Export Formats**: PDF, DOCX, TXT

6. **🖥️ User-Friendly Web Interface**
   - Modern, clean Google Material Design
   - Real-time progress tracking with stage-by-stage updates
   - Tabbed report viewer (Transcript, Summary, Timeline, Scenes)
   - One-click download buttons

### 🌟 Additional Features (Beyond Requirements)

1. **🤖 AI-Powered Analysis (NEW)**
   - Local LLM integration (Llama 3.2 3B Instruct)
   - Automatic summary generation
   - Intelligent key point extraction with timestamps
   - Privacy-focused (runs locally, no cloud API required)
   - Configurable AI features (can be enabled/disabled)

2. **💬 Interactive Q&A Chat (NEW)**
   - Ask questions about video content
   - Time-range specific queries ("What happened between 1-2 minutes?")
   - Natural language understanding
   - Context-aware responses using transcript + scene data
   - Conversational interface

3. **📑 Enhanced Reporting (NEW)**
   - AI Summary section in reports
   - Table of Contents for easy navigation
   - Scene Analysis timeline
   - Professional formatting with icons
   - Optional AI content inclusion (checkbox in export)

4. **🎨 Advanced UI Features (NEW)**
   - 6 tabbed sections (Transcript, Summary, Timeline, Scenes, AI Summary, Q&A Chat)
   - Real-time chat interface
   - Scene thumbnails with timestamps
   - Responsive design for all screen sizes
   - No scrollbar issues (optimized layouts)

5. **⚡ Performance Optimizations (NEW)**
   - Efficient memory management
   - Parallel processing pipelines
   - Smart caching
   - Background job processing
   - Session-based file management

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB INTERFACE (Flask)                    │
│                     Port: 5000 (localhost)                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   MAIN APPLICATION LAYER                     │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ File Manager   │  │ Job Manager  │  │ Progress Tracker│ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐  ┌───────────────┐  ┌──────────────────┐
│ VIDEO PROCESSOR │  │  TRANSCRIBER  │  │ SCENE DETECTOR   │
│  (FFmpeg)       │  │  (Whisper)    │  │  (OpenCV/scdet)  │
└─────────────────┘  └───────────────┘  └──────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ JSON Export │  │ PDF/DOCX/TXT │  │ Caption Generator │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              AI LAYER (OPTIONAL - LOCAL LLM)                 │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │ Llama 3.2 3B     │  │ LLM Processor                  │  │
│  │ (llama-cpp)      │  │ • Summary Generation           │  │
│  │                  │  │ • Key Points Extraction        │  │
│  │ ~2GB Model       │  │ • Q&A Chat                     │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

```
INPUT VIDEO
    │
    ├─→ [1] Download (if URL)
    │       ↓
    ├─→ [2] Scene Detection (parallel)
    │       • Extract key frames
    │       • Detect transitions
    │       ↓
    ├─→ [3] Audio Extraction
    │       ↓
    ├─→ [4] Transcription (Whisper)
    │       • Generate text + timestamps
    │       • Create SRT captions
    │       ↓
    ├─→ [5] Caption Burning (FFmpeg)
    │       • Overlay captions on video
    │       ↓
    ├─→ [6] Report Generation
    │       • Build JSON master report
    │       • Generate summaries
    │       ↓
    └─→ [7] AI Analysis (Optional)
            • Generate AI summary
            • Extract key points
            ↓
OUTPUT: Captioned Video + Reports + AI Insights
```

---

## 💾 Installation Guide

### Prerequisites

#### 1. **Python 3.8 or higher**
```bash
# Check Python version
python --version  # Should be 3.8+
```

#### 2. **FFmpeg** (Required for video processing)

**Windows:**
```bash
# Download from: https://ffmpeg.org/download.html
# Or use Chocolatey:
choco install ffmpeg

# Verify installation:
ffmpeg -version
```

**macOS:**
```bash
brew install ffmpeg

# Verify:
ffmpeg -version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg

# Verify:
ffmpeg -version
```

#### 3. **Git** (To clone repository)
```bash
git --version  # Should be installed
```

### Installation Steps

#### Step 1: Clone Repository
```bash
# Clone the project
git clone <repository-url>
cd VEDIO_CAPTION&REPORT_GENERATOR

# Or if you have a ZIP file:
# Extract and navigate to the folder
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

#### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# This installs:
# - Flask (web framework)
# - OpenAI Whisper (transcription)
# - OpenCV (video processing)
# - PySceneDetect (scene detection)
# - yt-dlp (YouTube download)
# - gdown (Google Drive download)
# - llama-cpp-python (local LLM - optional)
# - And other dependencies...
```

#### Step 4: Download AI Model (Optional - for AI features)
```bash
# Download Llama 3.2 3B model (~2GB)
python download_model.py

# This will:
# 1. Create 'models' folder
# 2. Download llama-3.2-3b-instruct.Q4_K_M.gguf
# 3. Configure model path in .env

# Skip this if you don't want AI features
```

#### Step 5: Configure Environment (Optional)
```bash
# Copy example config
cp .env.example .env

# Edit .env for customization:
# - Whisper model size (base/small/medium/large)
# - Caption styling
# - AI model settings
# - Output paths

# Default settings work fine for most users
```

#### Step 6: Verify Installation
```bash
# Run tests
python -c "import whisper; print('Whisper OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import flask; print('Flask OK')"

# All should print "OK"
```

### Quick Start

```bash
# 1. Activate virtual environment (if not already active)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 2. Run the application
python app.py

# 3. Open browser
# Navigate to: http://localhost:5000

# 4. Upload a video and click "Process Video"
```

---

## 📖 Usage Guide

### Web Interface

#### 1. **Start Application**
```bash
python app.py
```

Output:
```
============================================================
🎬 Meeting Video Captioning - Web Application
============================================================

🚀 Starting Flask server...
📡 Server URL: http://localhost:5000
📡 Or access from network: http://<your-ip>:5000

💡 Press Ctrl+C to stop the server
============================================================

 * Running on http://127.0.0.1:5000
```

#### 2. **Upload Video**

**Option A: Drag and Drop**
- Drag video file to upload area
- Supported: MP4, MOV, AVI, WebM, MKV

**Option B: Click to Browse**
- Click "Choose File" button
- Select video from file browser

**Option C: Paste URL**
- YouTube: `https://youtube.com/watch?v=...`
- Google Drive: `https://drive.google.com/file/d/...`
- Dropbox: `https://www.dropbox.com/s/...`
- Direct video link: `https://example.com/video.mp4`

#### 3. **Process Video**
Click "🎬 Process Video" button

**Real-time Progress Tracking:**
```
Stage 1: Downloading video...          [████████░░] 80%
Stage 2: Detecting scenes...           [██████████] 100%
Stage 3: Extracting audio...           [█░░░░░░░░░] 10%
Stage 4: Transcribing audio...         [░░░░░░░░░░] 0%
Stage 5: Generating captions...        [░░░░░░░░░░] 0%
Stage 6: Creating report...            [░░░░░░░░░░] 0%
Stage 7: Generating AI summary...      [░░░░░░░░░░] 0%
```

#### 4. **View Results**

**Report Viewer - 6 Tabs:**

1. **📄 Transcript**
   - Complete word-for-word transcription
   - Searchable text

2. **📊 Summary**
   - Video statistics (duration, scenes, sections)
   - Processing information
   - High-level overview

3. **🕐 Timeline**
   - All captions with timestamps
   - Format: `[00:00:15 → 00:00:18] Caption text`
   - Scrollable list

4. **🎬 Scenes**
   - Visual thumbnails of scene changes
   - Timestamp for each scene
   - Click to see frame

5. **🤖 AI Summary** (if enabled)
   - AI-generated executive summary
   - Extracted key points with timestamps
   - Intelligent insights

6. **💬 Q&A Chat** (if enabled)
   - Ask questions about video
   - Examples:
     - "What is this video about?"
     - "What happened between 1-2 minutes?"
     - "Summarize the key points"
     - "When was X mentioned?"

#### 5. **Download Outputs**

**Available Downloads:**

1. **📹 Video with Captions**
   - Original video with burned-in captions
   - Same format as input
   - Captions permanently visible

2. **📝 SRT Captions**
   - Subtitle file
   - Use with any video player
   - Standard SRT format

3. **📄 Report (PDF/DOCX/TXT)**
   - Click "Download" button
   - Choose format:
     - **PDF**: Best for viewing/printing
     - **DOCX**: Editable in Microsoft Word
     - **TXT**: Plain text, universal compatibility
   - Optional: Include/exclude AI Summary (checkbox)

**Report Contents:**
```
📑 Table of Contents
🤖 AI-Generated Summary (optional)
📊 Summary
🔑 Key Points
🎬 Scene Analysis
📖 Detailed Analysis by Section
📄 Full Transcript
```

---

## 📁 Project Structure

```
VEDIO_CAPTION&REPORT_GENERATOR/
│
├── 📄 app.py                          # Main application entry point
├── 📄 download_model.py               # AI model downloader
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env                            # Configuration file
├── 📄 README.md                       # This file
│
├── 📁 meeting_captioning/             # Core package
│   ├── 📄 __init__.py
│   ├── 📄 main_app.py                # Main processing pipeline
│   │
│   ├── 📁 ai/                        # AI components (NEW)
│   │   ├── 📄 __init__.py
│   │   └── 📄 llm_processor.py      # LLM integration
│   │
│   ├── 📁 video/                     # Video processing
│   │   ├── 📄 __init__.py
│   │   ├── 📄 downloader.py         # YouTube/cloud downloads
│   │   ├── 📄 scene_detector.py     # Scene change detection
│   │   └── 📄 processor.py          # FFmpeg operations
│   │
│   ├── 📁 transcription/             # Audio transcription
│   │   ├── 📄 __init__.py
│   │   ├── 📄 transcriber.py        # Whisper integration
│   │   └── 📄 segmenter.py          # Segment processing
│   │
│   ├── 📁 captioning/                # Caption generation
│   │   ├── 📄 __init__.py
│   │   ├── 📄 caption_generator.py  # SRT creation
│   │   └── 📄 caption_burner.py     # Video overlay
│   │
│   ├── 📁 reporting/                 # Report generation
│   │   ├── 📄 __init__.py
│   │   ├── 📄 report_builder.py     # Report structure
│   │   └── 📄 json_exporter.py      # JSON output
│   │
│   ├── 📁 web/                       # Web interface
│   │   ├── 📄 __init__.py
│   │   └── 📄 flask_app.py          # Flask routes/API
│   │
│   └── 📁 utils/                     # Utilities
│       ├── 📄 __init__.py
│       ├── 📄 file_manager.py       # File operations
│       ├── 📄 logging_config.py     # Logging setup
│       └── 📄 error_handling.py     # Error management
│
├── 📁 static/                        # Web assets
│   ├── 📁 css/
│   │   ├── 📄 style.css             # Main styles
│   │   └── 📄 chat.css              # Chat interface
│   └── 📁 js/
│       └── 📄 app.js                 # Frontend logic
│
├── 📁 templates/                     # HTML templates
│   └── 📄 index.html                # Main page
│
├── 📁 outputs/                       # Generated files
│   └── 📁 session_*/                # Per-session folders
│       ├── 📁 video/                # Processed videos
│       ├── 📁 scenes/               # Scene frames
│       ├── 📁 captions/             # SRT files
│       └── 📁 reports/              # JSON/AI reports
│
├── 📁 models/                        # AI models (optional)
│   └── llama-3.2-3b-instruct.Q4_K_M.gguf  (~2GB)
│
└── 📁 logs/                          # Application logs
    └── meeting_captioning_*.log
```

---

## 🔧 Component Details

### 1. Main Application (`main_app.py`)

**Purpose**: Orchestrates entire processing pipeline

**Key Methods**:
```python
process_video(video_path: str) -> dict:
    """
    Main processing pipeline:
    1. Download video (if URL)
    2. Detect scenes
    3. Extract audio
    4. Transcribe with Whisper
    5. Generate captions
    6. Burn captions to video
    7. Build report
    8. Generate AI summary (optional)
    """
```

**Progress Stages**:
- 0-10%: Video download/validation
- 10-30%: Scene detection
- 30-40%: Audio extraction
- 40-70%: Transcription
- 70-80%: Caption generation
- 80-90%: Report building
- 90-100%: AI analysis

### 2. Video Downloader (`video/downloader.py`)

**Supported Sources**:
- **YouTube**: Uses `yt-dlp` for reliable downloads
- **Google Drive**: Direct file download with `gdown`
- **Dropbox**: Public link downloads
- **Direct URLs**: Any direct video link

**Features**:
- Progress tracking
- Format selection (best quality)
- Metadata extraction
- Error handling

### 3. Scene Detector (`video/scene_detector.py`)

**Algorithm**: Content-aware scene change detection

**Methods**:
- **Threshold-based**: Detects significant frame differences
- **Adaptive**: Adjusts to video content
- **Efficient**: Parallel processing

**Output**:
- Scene timestamps
- Key frame extraction
- Thumbnail generation

### 4. Transcriber (`transcription/transcriber.py`)

**Engine**: OpenAI Whisper

**Models** (configurable):
- `base`: Fast, good for clear audio
- `small`: Balanced speed/accuracy
- `medium`: High accuracy
- `large`: Best accuracy, slower

**Features**:
- Word-level timestamps
- Multi-language support
- Speaker diarization (optional)
- Punctuation restoration

**Output Format**:
```json
{
  "text": "Complete transcription",
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Hello everyone"
    }
  ]
}
```

### 5. Caption Generator (`captioning/caption_generator.py`)

**SRT Format**:
```srt
1
00:00:00,000 --> 00:00:03,500
Hello everyone

2
00:00:03,500 --> 00:00:07,200
Welcome to this meeting
```

**Features**:
- Automatic timing
- Text wrapping (max characters per line)
- UTF-8 support (all languages)
- Standardized formatting

### 6. Caption Burner (`captioning/caption_burner.py`)

**FFmpeg Integration**: Burns captions permanently into video

**Styling Options** (configurable in `.env`):
```python
CAPTION_FONT = "Arial"
CAPTION_SIZE = 24
CAPTION_COLOR = "white"
CAPTION_BG_COLOR = "black@0.5"  # Semi-transparent
CAPTION_POSITION = "bottom"
```

**Process**:
```
Original Video + SRT File → FFmpeg → Captioned Video
```

### 7. Report Builder (`reporting/report_builder.py`)

**Report Structure**:
```python
class Report:
    title: str                    # Video title
    date: datetime               # Processing date
    video_path: Path             # Original video
    duration: float              # Video length
    summary: str                 # High-level summary
    key_points: List[str]        # Important moments
    full_transcript: str         # Complete text
    scenes: List[Scene]          # Scene objects
    sections: List[Section]      # Transcript sections
    metadata: dict               # Additional info
```

### 8. AI Processor (`ai/llm_processor.py`) - NEW

**Model**: Llama 3.2 3B Instruct (quantized, ~2GB)

**Capabilities**:

1. **Summary Generation**:
```python
generate_summary(max_tokens=300) -> str:
    """
    Creates concise executive summary
    Returns: 3-4 sentence overview
    """
```

2. **Key Points Extraction**:
```python
generate_key_points(max_points=5) -> List[str]:
    """
    Extracts important moments with timestamps
    Returns: ["[0:15] First point", ...]
    """
```

3. **Q&A Chat**:
```python
answer_question(question: str) -> str:
    """
    Answers questions about video content
    Supports time-range queries
    Returns: Natural language answer
    """
```

**Features**:
- Runs locally (privacy-focused)
- No API costs
- Context-aware (uses transcript + scenes)
- Time-range query support
- Conversational responses

### 9. Web Interface (`web/flask_app.py`)

**Routes**:
```python
GET  /                    # Main page
POST /api/upload          # File upload
POST /api/upload_url      # URL submission
GET  /api/status/<job_id> # Progress tracking
GET  /api/download/<path> # File download
GET  /api/transcript/...  # Transcript data
POST /api/qa              # Q&A chat
```

**Frontend** (`static/js/app.js`):
- Real-time progress updates
- Tabbed report viewer
- Chat interface
- PDF generation (client-side)
- File downloads

---

## 🌟 Additional Features (Beyond Requirements)

### 1. AI-Powered Analysis

**Implementation**: Local Llama 3.2 3B model via llama-cpp-python

**Benefits**:
- **Privacy**: All processing happens locally
- **Cost**: No API fees (one-time model download)
- **Speed**: Fast inference on CPU (6 threads)
- **Quality**: Competitive with cloud APIs for summaries

**Use Cases**:
- Executive summaries for long meetings
- Quick key point extraction
- Understanding video without watching
- Searchable insights

### 2. Interactive Q&A Chat

**Capabilities**:
- General questions: "What is this video about?"
- Time-specific: "What happened at 2 minutes?"
- Time-range: "Summarize 1 min to 3 min"
- Topic search: "When was X mentioned?"

**Technical Details**:
- Uses transcript + scene timeline
- Filters relevant sections for queries
- Natural language understanding
- Context-aware responses

**Example Interactions**:
```
User: "What happened between 1 min to 2 min?"
AI: "Between 1:00 and 2:00, the speaker discussed gold price predictions. 
     They mentioned that their initial forecast of $4200 has been reached, 
     but the rally happened faster than expected (50-60% in 6-8 months 
     instead of 35-40% annually). This rapid speed surprised everyone."

User: "When was the price mentioned?"
AI: "The price of $4200 was mentioned at around 0:10."
```

### 3. Enhanced Report Formats

**Improvements**:
- Professional headers with metadata box
- Table of Contents
- Icon-based section headers (🤖📊🔑🎬)
- Scene Analysis timeline
- Formatted TXT with ASCII art
- Separate AI content (can be excluded)

**PDF Enhancements**:
- Multi-page support with auto-pagination
- Proper font sizing and spacing
- Color-coded AI sections (blue)
- Compact yet readable layout

### 4. Advanced UI/UX

**Material Design**:
- Clean, modern interface
- Responsive layout
- Smooth animations
- Progress indicators

**User Experience**:
- Drag-and-drop upload
- Real-time feedback
- Error messages (user-friendly)
- No page reloads (AJAX)

### 5. Session Management

**File Organization**:
```
outputs/session_20251211_174205/
├── video/
│   ├── original.mp4
│   └── captioned.mp4
├── scenes/
│   ├── scene_001.jpg
│   ├── scene_002.jpg
│   └── ...
├── captions/
│   └── captions.srt
└── reports/
    ├── report.json
    └── ai_summary.json
```

**Benefits**:
- Organized outputs
- Easy cleanup
- Parallel processing support
- Session recovery

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# === Whisper Configuration ===
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
# Larger = more accurate but slower

# === Video Processing ===
SCENE_THRESHOLD=30.0  # Scene detection sensitivity (0-100)
# Higher = fewer scenes (only major changes)

# === Caption Styling ===
CAPTION_FONT=Arial
CAPTION_SIZE=24
CAPTION_COLOR=white
CAPTION_BG_COLOR=black@0.5  # @ = opacity (0.0-1.0)
CAPTION_POSITION=bottom  # Options: top, center, bottom

# === AI Model ===
LLM_MODEL_PATH=models/llama-3.2-3b-instruct.Q4_K_M.gguf
LLM_THREADS=6  # CPU threads for inference
LLM_CONTEXT_SIZE=8192  # Token context window

# === Output Paths ===
OUTPUT_DIR=outputs
TEMP_DIR=temp
LOG_DIR=logs

# === Server ===
FLASK_PORT=5000
FLASK_DEBUG=False  # Set True for development
```

### Model Selection Guide

**Whisper Models**:
| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39M | Fastest | Good | Testing, previews |
| base | 74M | Fast | Good | Clear audio, English |
| small | 244M | Medium | Better | Most meetings |
| medium | 769M | Slow | Great | Important content |
| large | 1550M | Slowest | Best | Critical accuracy |

**Recommendation**: Start with `base`, upgrade to `small` if needed.

---

## 🐛 Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found
```
Error: FFmpeg not found
```

**Solution**:
```bash
# Windows:
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg

# Verify:
ffmpeg -version
```

#### 2. Whisper Model Download Fails
```
Error: Failed to download Whisper model
```

**Solution**:
```bash
# Manual download:
python -c "import whisper; whisper.load_model('base')"

# Or specify cache location:
export WHISPER_CACHE=./models
```

#### 3. Out of Memory
```
Error: Killed / MemoryError
```

**Solution**:
- Use smaller Whisper model (`tiny` or `base`)
- Process shorter videos
- Close other applications
- Increase system swap space

#### 4. AI Model Not Loading
```
Error: Model not found
```

**Solution**:
```bash
# Re-download model:
python download_model.py

# Check model path in .env:
# LLM_MODEL_PATH=models/llama-3.2-3b-instruct.Q4_K_M.gguf

# Verify file exists:
ls -lh models/
```

#### 5. YouTube Download Fails
```
Error: Unable to download video
```

**Solution**:
```bash
# Update yt-dlp:
pip install --upgrade yt-dlp

# Check video is public (not private/restricted)

# Try alternative URL format
```

#### 6. Port Already in Use
```
Error: Address already in use
```

**Solution**:
```bash
# Find and kill process using port 5000:
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Or use different port:
export FLASK_PORT=5001
python app.py
```

### Debugging

**Enable Debug Mode**:
```bash
# Set in .env:
FLASK_DEBUG=True

# Or run with:
python app.py --debug
```

**Check Logs**:
```bash
# View latest log:
tail -f logs/meeting_captioning_*.log

# Search for errors:
grep ERROR logs/*.log
```

**Verbose Output**:
```bash
# Run with detailed logging:
python app.py --verbose
```

---

## 📊 Performance Notes

### Processing Times (Approximate)

**Hardware**: Intel i5, 16GB RAM, No GPU

| Video Length | Scene Detection | Transcription (base) | Total Time |
|--------------|----------------|---------------------|------------|
| 5 minutes | 10 sec | 2 min | ~3 min |
| 15 minutes | 20 sec | 5 min | ~7 min |
| 30 minutes | 30 sec | 10 min | ~12 min |
| 1 hour | 1 min | 20 min | ~25 min |
| 2 hours | 2 min | 40 min | ~50 min |

**Factors Affecting Speed**:
- Whisper model size (larger = slower but more accurate)
- Video resolution (4K takes longer than 720p)
- Scene complexity (more scenes = more processing)
- AI features enabled/disabled

### Optimization Tips

1. **Faster Processing**:
   - Use `tiny` or `base` Whisper model
   - Increase `SCENE_THRESHOLD` (fewer scenes)
   - Disable AI features if not needed

2. **Better Quality**:
   - Use `medium` or `large` Whisper model
   - Lower `SCENE_THRESHOLD` (more scenes)
   - Enable AI analysis

3. **Balance**:
   - `small` Whisper model
   - Default scene threshold (30.0)
   - Enable AI for important videos

### Resource Requirements

**Minimum**:
- CPU: Dual-core 2GHz
- RAM: 4GB
- Storage: 10GB free

**Recommended**:
- CPU: Quad-core 2.5GHz+
- RAM: 8GB+
- Storage: 20GB+ free
- SSD (faster I/O)

**With AI Features**:
- RAM: 8GB+ (model requires ~3GB)
- Storage: 12GB+ (model is ~2GB)

---
## 🔒 Privacy & Security

**Data Handling**:
- All processing happens locally (except Whisper API if configured)
- No video data sent to external servers (except for download)
- Session files stored locally, can be deleted
- AI analysis runs completely offline

**Best Practices**:
- Use local Whisper model for sensitive content
- Enable local LLM (no cloud API calls)
- Delete session folders after use if needed
- Don't share output files with sensitive info

---

## 🙏 Acknowledgments

**Technologies Used**:
- **OpenAI Whisper**: Speech-to-text transcription
- **FFmpeg**: Video processing and caption burning
- **PySceneDetect**: Scene change detection
- **Flask**: Web framework
- **Llama.cpp**: Local LLM inference
- **yt-dlp**: YouTube video downloads
- **jsPDF**: Client-side PDF generation

**AI Model**:
- **Llama 3.2 3B Instruct** by Meta AI
- Quantized by bartowski (GGUF format)

---

## 📊 Project Statistics

- **Total Lines of Code**: ~8,000+
- **Python Files**: 25+
- **Dependencies**: 20+
- **Processing Stages**: 7
- **Supported Formats**: 5+
- **Export Formats**: 3 (PDF, DOCX, TXT)
- **UI Tabs**: 6
- **AI Features**: 3 (Summary, Key Points, Q&A)

---

**🎉 Thank you for using the Meeting Video Captioning & Documentation System!**

For the latest updates and documentation, visit the GitHub repository.

---

*Last Updated: December 11, 2025*
*Version: 2.0 (AI-Enhanced Edition)*
