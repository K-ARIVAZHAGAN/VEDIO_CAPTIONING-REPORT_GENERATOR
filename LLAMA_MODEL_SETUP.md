# 🦙 Llama Model Setup Guide

## Overview
The AI summary feature requires the **Llama 3.2 3B** model file. This is **optional** - the system works without it (you'll just skip AI summaries).

**Note:** The model file is **~2GB** and takes time to download.

---

## 📥 Option 1: Quick Download (Recommended)

### Method A: Direct Google Drive Download (Fastest)

**Pre-uploaded model available on Google Drive (provided by project maintainer):**

1. **Download from Google Drive:**
   - Visit: https://drive.google.com/drive/folders/14SIbTmyqwIUZ71AbfUs5TAYXIbvm9IjD?usp=drive_link
   - Click on `llama-3.2-3b-instruct.Q4_K_M.gguf`
   - Click Download button (⬇️)
   - Save to your Downloads folder

2. **Move to project models folder:**
   ```bash
   # Windows PowerShell
   mkdir models -ErrorAction SilentlyContinue
   Move-Item -Path "$env:USERPROFILE\Downloads\llama-3.2-3b-instruct.Q4_K_M.gguf" -Destination "models\" -Force

   # Mac/Linux
   mkdir -p models
   mv ~/Downloads/llama-3.2-3b-instruct.Q4_K_M.gguf models/
   ```

3. **Verify the file:**
   ```bash
   # Windows PowerShell
   Get-ChildItem models/

   # Mac/Linux
   ls -lh models/
   ```

**✅ This is the fastest method!** File is already available on Google Drive.

---

### Method B: Download from Hugging Face

### Step 1: Create models directory
```bash
# Windows PowerShell
mkdir models

# Mac/Linux
mkdir -p models
```

### Step 2: Download the model file
**Direct Download Link:**
```
https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf
```

**Note:** Hugging Face download may be slower depending on your location. Consider using the Google Drive link above for faster download.

**Methods:**

**Option A: Browser Download**
1. Click the link above
2. Save as: `llama-3.2-3b-instruct.Q4_K_M.gguf`
3. Move to `models/` folder in project

**Option B: Command Line (Windows)**
```powershell
# Using PowerShell
Invoke-WebRequest -Uri "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf" -OutFile "models/llama-3.2-3b-instruct.Q4_K_M.gguf"
```

**Option C: Command Line (Mac/Linux)**
```bash
# Using wget
wget -O models/llama-3.2-3b-instruct.Q4_K_M.gguf "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"

# OR using curl
curl -L -o models/llama-3.2-3b-instruct.Q4_K_M.gguf "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
```

### Step 3: Verify the download
```bash
# Windows PowerShell
Get-ChildItem models/

# Mac/Linux
ls -lh models/
```

**Expected output:**
```
llama-3.2-3b-instruct.Q4_K_M.gguf  (~2GB)
```

---

## 📥 Option 2: Using Hugging Face CLI

### Step 1: Install Hugging Face CLI
```bash
pip install huggingface-hub
```

### Step 2: Download model
```bash
huggingface-cli download bartowski/Llama-3.2-3B-Instruct-GGUF Llama-3.2-3B-Instruct-Q4_K_M.gguf --local-dir models --local-dir-use-symlinks False
```

### Step 3: Rename file
```bash
# Windows PowerShell
Rename-Item -Path "models\Llama-3.2-3B-Instruct-Q4_K_M.gguf" -NewName "llama-3.2-3b-instruct.Q4_K_M.gguf"

# Mac/Linux
mv models/Llama-3.2-3B-Instruct-Q4_K_M.gguf models/llama-3.2-3b-instruct.Q4_K_M.gguf
```

---

## 📥 Option 3: Transfer from Another System

If you already have the model on another computer:

### Step 1: Locate the file
```bash
# On the source system
# Windows: C:\Users\<username>\Downloads\VEDIO_CAPTION&REPORT_GENERATOR\models\llama-3.2-3b-instruct.Q4_K_M.gguf
# Mac: /Users/<username>/Downloads/VEDIO_CAPTIONING-REPORT_GENERATOR/models/llama-3.2-3b-instruct.Q4_K_M.gguf
```

### Step 2: Copy to target system

**Option A: USB Drive**
1. Copy file to USB drive
2. Plug into target system
3. Copy to `models/` folder

**Option B: Network Transfer (Same WiFi)**
```bash
# On source system (Mac/Linux) - start simple HTTP server
cd models
python3 -m http.server 8888

# On target system - download
wget http://<source-ip>:8888/llama-3.2-3b-instruct.Q4_K_M.gguf -P models/
```

**Option C: Cloud Storage**
1. Upload to Google Drive / Dropbox
2. Download on target system
3. Move to `models/` folder

---

## ✅ Verification

After setup, verify the model works:

```bash
# Activate virtual environment first
# Windows: .venv\Scripts\Activate.ps1
# Mac/Linux: source .venv/bin/activate

# Test model loading
python -c "from meeting_captioning.ai.llm_processor import LLMProcessor; print('✅ Model loads successfully' if LLMProcessor() else '❌ Model failed')"
```

**Expected output:**
```
✅ Model loads successfully
```

---

## 🚀 Run Application

After model is set up:

```bash
# Windows PowerShell
python app.py

# Mac/Linux
python app.py
```

Access at: **http://localhost:5000**

---

## ⚠️ Troubleshooting

### Issue: "Failed to load model"
**Solution:** Check file path and name exactly:
```
models/llama-3.2-3b-instruct.Q4_K_M.gguf
```

### Issue: SSL Certificate Error during download
**Solution:** Use the browser download method, or:
```bash
# Mac/Linux - disable SSL verification temporarily
wget --no-check-certificate -O models/llama-3.2-3b-instruct.Q4_K_M.gguf "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
```

### Issue: Slow download
**Solution:** 
- Use browser download and leave it running
- File is 2GB, may take 10-30 minutes on slow connections
- Consider transferring from another system if already downloaded

### Issue: "File not found" error
**Solution:** Check exact filename matches:
```bash
# Should be exactly this name:
llama-3.2-3b-instruct.Q4_K_M.gguf

# NOT:
Llama-3.2-3B-Instruct-Q4_K_M.gguf  # Wrong case
llama-3.2-3b-instruct.gguf          # Missing Q4_K_M
```

---

## 🎯 System Works Without Model

**Important:** If you skip this setup:
- ✅ Video processing works
- ✅ Audio extraction works
- ✅ Transcription works
- ✅ Caption generation works
- ✅ Reports generated (JSON)
- ❌ AI summary skipped (gracefully)

The system will show: **"AI features not available (model not loaded)"**

---

## 📊 Disk Space Requirements

- **Model file:** ~2GB
- **Virtual environment:** ~3GB
- **Total needed:** ~5GB free space

---

## 🔗 Alternative Models (Optional)

Want a different model? Change in `meeting_captioning/config.py`:

```python
# Smaller model (faster, less accurate)
LLM_MODEL_PATH = "models/llama-3.2-1b-instruct.Q4_K_M.gguf"
# Download from: https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF

# Larger model (slower, more accurate)
LLM_MODEL_PATH = "models/llama-3.2-7b-instruct.Q4_K_M.gguf"
# Download from: https://huggingface.co/bartowski/Llama-3.2-7B-Instruct-GGUF
```

---

## 📝 Quick Summary for Other Systems

**Minimal steps:**
1. Download model from Google Drive: https://drive.google.com/drive/folders/14SIbTmyqwIUZ71AbfUs5TAYXIbvm9IjD?usp=drive_link
2. Move file to `models/llama-3.2-3b-instruct.Q4_K_M.gguf`
3. Run: `python app.py`

**Alternative (if Google Drive unavailable):**
1. Ensure `models/` folder exists
2. Download: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf
3. Save as: `models/llama-3.2-3b-instruct.Q4_K_M.gguf`
4. Run: `python app.py`

**That's it!** 🎉
