# 🚀 Quick Start Guide

Get started with Movie List Maker in 5 minutes!

## Prerequisites

- Python 3.8+
- Tesseract OCR
- FFmpeg

## Installation

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/Movie-List-Maker.git
cd Movie-List-Maker

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr ffmpeg
```

**macOS:**
```bash
brew install tesseract ffmpeg
```

**Windows:**
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- FFmpeg: https://ffmpeg.org/download.html

## First Run

```bash
# Process a video
python main.py your_video.mp4 --oleada 1

# The script will:
# ✓ Extract frames from video
# ✓ Run OCR on frames
# ✓ Transcribe audio with Whisper
# ✓ Match and validate titles
# ✓ Prompt you for low-confidence matches
# ✓ Generate markdown output
# ✓ Create Quarto website
```

## Common Commands

```bash
# Fast processing (tiny Whisper model)
python main.py video.mp4 --oleada 1 --whisper-model tiny

# Process multiple videos
python main.py video1.mp4 video2.mp4 video3.mp4 --starting-oleada 1

# Non-interactive mode
python main.py video.mp4 --oleada 1 --no-interactive

# Save frames for debugging
python main.py video.mp4 --oleada 1 --save-frames

# Spanish language videos
python main.py video.mp4 --oleada 1 --language es

# Auto-detect Spanish/English (default)
python main.py video.mp4 --oleada 1
```

## Build Website

```bash
cd quarto_site
quarto render
```

Website will be in `quarto_site/docs/`

## Troubleshooting

**"Tesseract not found"**
```bash
# Verify installation
tesseract --version
```

**"FFmpeg not found"**
```bash
# Verify installation
ffmpeg -version
```

**Memory issues**
```bash
# Use smaller Whisper model
python main.py video.mp4 --oleada 1 --whisper-model tiny
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [OPTIMIZATION.md](OPTIMIZATION.md) for performance tuning
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for OS-specific setup

---

**Happy Processing! 🎬**
