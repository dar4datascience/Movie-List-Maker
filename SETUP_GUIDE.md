# 🛠️ Setup Guide - Movie List Maker

Complete setup instructions for different operating systems.

## Table of Contents

1. [Linux Setup](#linux-setup)
2. [macOS Setup](#macos-setup)
3. [Windows Setup](#windows-setup)
4. [Verification](#verification)
5. [First Run](#first-run)

---

## Linux Setup

### Ubuntu/Debian

```bash
# 1. Update package list
sudo apt-get update

# 2. Install system dependencies
sudo apt-get install -y python3 python3-pip python3-venv tesseract-ocr ffmpeg

# 3. Clone repository
git clone https://github.com/yourusername/Movie-List-Maker.git
cd Movie-List-Maker

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 6. Install Quarto (optional)
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.549/quarto-1.4.549-linux-amd64.deb
sudo dpkg -i quarto-1.4.549-linux-amd64.deb
```

### Fedora/RHEL/CentOS

```bash
# 1. Install system dependencies
sudo dnf install -y python3 python3-pip tesseract ffmpeg

# 2. Follow steps 3-6 from Ubuntu instructions above
```

### Arch Linux

```bash
# 1. Install system dependencies
sudo pacman -S python python-pip tesseract ffmpeg

# 2. Follow steps 3-6 from Ubuntu instructions above
```

---

## macOS Setup

### Using Homebrew

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install system dependencies
brew install python tesseract ffmpeg

# 3. Clone repository
git clone https://github.com/yourusername/Movie-List-Maker.git
cd Movie-List-Maker

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 6. Install Quarto (optional)
brew install --cask quarto
```

---

## Windows Setup

### Method 1: Using Chocolatey (Recommended)

```powershell
# 1. Install Chocolatey (run PowerShell as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Install dependencies
choco install -y python tesseract ffmpeg

# 3. Clone repository (in regular PowerShell/CMD)
git clone https://github.com/yourusername/Movie-List-Maker.git
cd Movie-List-Maker

# 4. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 5. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 6. Install Quarto (optional)
choco install -y quarto
```

### Method 2: Manual Installation

#### Install Python
1. Download Python 3.8+ from https://www.python.org/downloads/
2. Run installer, check "Add Python to PATH"
3. Verify: `python --version`

#### Install Tesseract
1. Download from https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Environment Variables → System Variables → Path → Edit
   - Add: `C:\Program Files\Tesseract-OCR`

#### Install FFmpeg
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH (same process as Tesseract)

#### Setup Project
```cmd
# Clone repository
git clone https://github.com/yourusername/Movie-List-Maker.git
cd Movie-List-Maker

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

#### Install Quarto (Optional)
Download from https://quarto.org/docs/get-started/

---

## Verification

### Verify System Dependencies

```bash
# Check Python
python --version  # Should be 3.8+

# Check Tesseract
tesseract --version  # Should show version info

# Check FFmpeg
ffmpeg -version  # Should show version info

# Check Quarto (optional)
quarto --version  # Should show version info
```

### Verify Python Packages

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Check installations
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import pytesseract; print('pytesseract: OK')"
python -c "import whisper; print('Whisper: OK')"
```

---

## First Run

### Test with Sample Video

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Run with a test video
python main.py path/to/test_video.mp4 --oleada 1 --whisper-model tiny

# This will:
# 1. Extract frames from video
# 2. Run OCR on frames
# 3. Transcribe audio with Whisper
# 4. Match and validate titles
# 5. Generate markdown output
# 6. Create Quarto website
```

### Expected Output

```
======================================================================
🎬 Movie List Maker
======================================================================
Videos to process: 1
Whisper model: tiny
Frame interval: 30
Confidence threshold: 90.0%
Interactive mode: Yes
======================================================================

======================================================================
🎬 Processing Oleada 01: test_video.mp4
======================================================================

📹 Step 1/5: Extracting frames from video...
Processing video: test_video.mp4
FPS: 30.0, Total frames: 900
Extracted 30 frames from 900 total frames

🔍 Step 2/5: Running OCR on 30 frames...
   Found 5 potential titles via OCR

🎤 Step 3/5: Transcribing audio with Whisper...
Loading Whisper model: tiny
Whisper model loaded successfully
Transcribing audio from: test_video.mp4
Transcription complete. Detected language: en
   Found 5 potential titles via audio

✅ Step 4/5: Matching and validating titles...

📝 Step 5/5: Generating markdown output...
✅ Markdown saved to: output/oleada-01.qmd

======================================================================
✨ Processing complete! Found 5 movies
======================================================================
```

---

## Troubleshooting

### "Tesseract not found"

**Linux/macOS:**
```bash
which tesseract  # Find installation path
export PATH=$PATH:/path/to/tesseract
```

**Windows:**
Add Tesseract to PATH or set environment variable:
```python
# In ocr_extractor.py, add:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### "FFmpeg not found"

Ensure FFmpeg is in PATH:
```bash
# Linux/macOS
which ffmpeg

# Windows
where ffmpeg
```

### Virtual Environment Issues

**Linux/macOS:**
```bash
# Deactivate and recreate
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
deactivate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Permission Errors (Linux/macOS)

```bash
# Don't use sudo with pip
# Instead, ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ Verify all dependencies are installed
2. ✅ Test with a sample video
3. 📖 Read the [README.md](README.md) for usage examples
4. 🚀 Process your movie videos!
5. 🌐 Build and deploy your Quarto website

---

**Need Help?** Open an issue on GitHub!
