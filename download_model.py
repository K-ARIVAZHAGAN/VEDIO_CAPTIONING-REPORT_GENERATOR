"""
Download Llama 3.2 3B Model for AI Features

This script downloads the Llama 3.2 3B Instruct GGUF model (~2 GB) from Hugging Face.
Run this once to enable AI summary and Q&A features.
"""

import os
import sys
import urllib.request
from pathlib import Path


def download_with_progress(url: str, output_path: Path):
    """Download file with progress bar."""
    
    def report_progress(count, block_size, total_size):
        percent = count * block_size * 100 / total_size
        downloaded_mb = count * block_size / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        sys.stdout.write(f"\rDownloading: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)")
        sys.stdout.flush()
    
    print(f"Downloading Llama 3.2 3B model to: {output_path}")
    print(f"From: {url}")
    print("This is a one-time download (~2 GB)...")
    print()
    
    try:
        urllib.request.urlretrieve(url, output_path, reporthook=report_progress)
        print("\n✅ Download complete!")
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def main():
    """Main function to download Llama 3.2 3B model."""
    
    # Determine paths
    project_root = Path(__file__).parent
    models_dir = project_root / "models"
    model_file = models_dir / "llama-3.2-3b-instruct.Q4_K_M.gguf"
    
    # Create models directory
    models_dir.mkdir(exist_ok=True)
    
    # Check if already downloaded
    if model_file.exists():
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"✅ Model already downloaded: {model_file}")
        print(f"   Size: {size_mb:.1f} MB")
        print()
        print("AI features are ready to use!")
        return
    
    print("=" * 60)
    print("  Llama 3.2 3B Model Download")
    print("=" * 60)
    print()
    print("This will download the Llama 3.2 3B Instruct model for AI features:")
    print("  • Automatic video summaries (much better accuracy)")
    print("  • Interactive Q&A about videos")
    print("  • Timeline-aware responses")
    print()
    print("Model details:")
    print("  • File: llama-3.2-3b-instruct.Q4_K_M.gguf")
    print("  • Size: ~2 GB")
    print("  • License: Llama 3.2 Community License")
    print("  • Source: Hugging Face")
    print()
    
    response = input("Download now? (y/n): ").strip().lower()
    if response != 'y':
        print("Download cancelled.")
        print()
        print("You can download manually from:")
        print("https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF")
        print(f"Place the file in: {models_dir}")
        return
    
    print()
    
    # Download URL
    url = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    
    # Download
    success = download_with_progress(url, model_file)
    
    if success:
        print()
        print("=" * 60)
        print("  Setup Complete!")
        print("=" * 60)
        print()
        print("✅ Llama 3.2 3B model is ready to use")
        print(f"   Location: {model_file}")
        print()
        print("Next steps:")
        print("  1. Run: python app.py")
        print("  2. Process a video")
        print("  3. Check the 'AI Summary' and 'Q&A' tabs (much better accuracy!)")
        print()
    else:
        print()
        print("Download failed. Please try:")
        print("  1. Check your internet connection")
        print("  2. Download manually from:")
        print("     https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF")
        print(f"  3. Place in: {models_dir}")


if __name__ == "__main__":
    main()
