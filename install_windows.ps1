# Windows Installation Script for Video Captioning System
# This script handles llama-cpp-python installation with pre-built wheels

Write-Host "🚀 Installing Video Captioning System on Windows..." -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "📌 Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version
Write-Host "✓ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Create virtual environment if not exists
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip
Write-Host ""

# Install llama-cpp-python with pre-built wheel (CPU version)
Write-Host "🤖 Installing llama-cpp-python (pre-built wheel)..." -ForegroundColor Cyan
pip install llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
Write-Host ""

# Install other requirements
Write-Host "📦 Installing remaining dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt
Write-Host ""

# Verify installation
Write-Host "✅ Verifying installation..." -ForegroundColor Cyan
python -c "import llama_cpp; print('✓ llama-cpp-python:', llama_cpp.__version__)"
python -c "from imageio_ffmpeg import get_ffmpeg_exe; print('✓ Bundled ffmpeg:', get_ffmpeg_exe())"
python -c "import whisper; print('✓ openai-whisper:', whisper.__version__)"
python -c "import cv2; print('✓ opencv-python:', cv2.__version__)"
Write-Host ""

Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Download the Llama model (if not already present):" -ForegroundColor White
Write-Host "      Place it in: models/llama-3.2-3b-instruct.Q4_K_M.gguf" -ForegroundColor White
Write-Host "   2. Run the application:" -ForegroundColor White
Write-Host "      python app.py" -ForegroundColor White
Write-Host ""
