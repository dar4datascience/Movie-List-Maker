# 🎬 Movie List Maker

A Python application that processes videos of movie covers with spoken titles, extracts text using OCR and speech recognition, validates matches, and generates beautiful Quarto websites with numbered movie lists.

## ✨ Features

- **Dual Extraction**: Combines OpenCV + Tesseract OCR with OpenAI Whisper for robust movie title extraction
- **Intelligent Validation**: String similarity matching with 90% confidence threshold
- **Interactive Review**: Prompts user for manual selection when confidence is low
- **Automated Website Generation**: Creates Quarto websites with Cosmos theme
- **GitHub Pages Ready**: Outputs to `docs/` directory for easy deployment
- **Timestamped Results**: Tracks when each movie appears in the video
- **Batch Processing**: Handle multiple videos (Oleadas) in one run

## 📋 Requirements

- Python 3.8+
- Tesseract OCR installed on system
- FFmpeg (for Whisper audio processing)
- Quarto CLI (for website generation)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Movie-List-Maker.git
cd Movie-List-Maker
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr ffmpeg
```

**macOS:**
```bash
brew install tesseract ffmpeg
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download FFmpeg: https://ffmpeg.org/download.html

### 5. Install Quarto (Optional, for website generation)

Download from: https://quarto.org/docs/get-started/

## 📖 Usage

### Basic Usage

Process a single video:

```bash
python main.py path/to/video.mp4 --oleada 1
```

### Process Multiple Videos

```bash
python main.py video1.mp4 video2.mp4 video3.mp4 --starting-oleada 1
```

### Advanced Options

```bash
# Use faster Whisper model (less accurate but quicker)
python main.py video.mp4 --oleada 1 --whisper-model tiny

# Non-interactive mode (auto-accept all matches)
python main.py video.mp4 --oleada 1 --no-interactive

# Save extracted frames for debugging
python main.py video.mp4 --oleada 1 --save-frames

# Custom frame extraction interval (higher = faster, fewer frames)
python main.py video.mp4 --oleada 1 --frame-interval 60

# Skip Quarto website generation
python main.py video.mp4 --oleada 1 --skip-quarto
```

### Full CLI Options

```
positional arguments:
  videos                Path(s) to video file(s) to process

optional arguments:
  --oleada OLEADA       Oleada number (for single video)
  --starting-oleada N   Starting oleada number for multiple videos (default: 1)
  --frame-interval N    Extract one frame every N frames (default: 30)
  --whisper-model {tiny,base,small,medium,large}
                        Whisper model size (default: base)
  --confidence-threshold FLOAT
                        Confidence threshold for auto-accepting matches (default: 0.90)
  --output-dir DIR      Output directory for intermediate files (default: output)
  --quarto-dir DIR      Quarto project directory (default: quarto_site)
  --no-interactive      Disable interactive prompts
  --save-frames         Save extracted frames to disk
  --skip-quarto         Skip Quarto website generation
```

## 🌐 Building the Quarto Website

After processing videos, build the website:

```bash
cd quarto_site
quarto render
```

The website will be generated in `quarto_site/docs/`.

### Deploy to GitHub Pages

1. Push repository to GitHub
2. Go to Settings → Pages
3. Set source to "Deploy from a branch"
4. Select branch: `main`, folder: `/docs`
5. Save and wait for deployment

## 🏗️ Project Structure

```
Movie-List-Maker/
├── src/
│   ├── __init__.py
│   ├── video_processor.py      # Frame extraction with OpenCV
│   ├── ocr_extractor.py         # Text extraction with Tesseract
│   ├── audio_transcriber.py     # Audio transcription with Whisper
│   ├── validator.py             # Confidence scoring and validation
│   ├── markdown_generator.py    # Markdown list generation
│   ├── quarto_generator.py      # Quarto website configuration
│   └── movie_processor.py       # Main orchestrator
├── main.py                      # CLI interface
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── output/                      # Generated markdown files
└── quarto_site/                 # Quarto website project
    ├── _quarto.yml              # Quarto configuration
    ├── index.qmd                # Home page
    ├── oleada-*.qmd             # Movie list pages
    ├── styles.css               # Custom styling
    └── docs/                    # Generated website (GitHub Pages)
```

## ⚡ Performance Optimization

### Lightweight Processing Options

The codebase is designed for efficiency. Here are optimization strategies:

#### 1. **Frame Extraction Optimization**
- **Default**: Extracts 1 frame every 30 frames (~1 fps at 30fps video)
- **Faster**: Use `--frame-interval 60` or higher
- **Trade-off**: Higher intervals may miss movies that appear briefly

#### 2. **Whisper Model Selection**
- **Tiny**: Fastest, ~1GB RAM, good for clear audio
- **Base** (default): Balanced speed/accuracy, ~1.5GB RAM
- **Small**: Better accuracy, ~2.5GB RAM
- **Medium/Large**: Best accuracy, 5-10GB RAM, much slower

#### 3. **Alternative Lightweight Approaches**

**Option A: OCR-Only Mode** (Fastest)
- Disable Whisper transcription
- Rely solely on visual text extraction
- Modify code to skip audio processing

**Option B: Audio-Only Mode** (No frame processing)
- Skip frame extraction and OCR
- Use only Whisper transcription
- Best when audio is clear and reliable

**Option C: Sparse Sampling**
- Extract frames only at specific intervals (e.g., every 5 seconds)
- Reduce OCR processing time significantly

**Option D: GPU Acceleration**
- Use CUDA-enabled Whisper for 5-10x speedup
- Install: `pip install openai-whisper[cuda]`
- Requires NVIDIA GPU with CUDA support

### Memory Usage

- **Tiny Whisper**: ~1GB RAM
- **Base Whisper**: ~1.5GB RAM
- **Frame Processing**: ~500MB per video
- **Total Recommended**: 4GB+ RAM

## 🔧 Troubleshooting

### Tesseract Not Found
```bash
# Verify installation
tesseract --version

# If not found, add to PATH or specify location
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
```

### Whisper Model Download Issues
Models are downloaded automatically on first use. Ensure internet connection.

### Low OCR Accuracy
- Increase video quality
- Adjust frame preprocessing in `video_processor.py`
- Use higher resolution source videos

### Memory Issues
- Use smaller Whisper model (`--whisper-model tiny`)
- Increase frame interval (`--frame-interval 60`)
- Process videos one at a time

## 📝 Output Format

### Markdown Example

```markdown
# Oleada 01 - Movie List

**Total Movies:** 3

---

1. **The Dark Knight** (Confidence: 98%, Time: 00:15)
2. **Inception** (Confidence: 92%, Time: 01:23)
3. **Interstellar** (Confidence: 87%, Time: 02:45)
   - 👤 User selected "Interstellar" from OCR: "Insterstellar" / Audio: "Interstellar"

---

*Generated by Movie List Maker*
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenCV**: Video processing
- **Tesseract OCR**: Text extraction
- **OpenAI Whisper**: Audio transcription
- **Quarto**: Website generation
- **Cosmos Theme**: Beautiful website styling

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Happy Movie Listing! 🎬🍿**
