# 🌍 Language Support - Movie List Maker

Automatic language detection for Spanish and English movie titles.

## Features

### Automatic Language Detection

The system automatically detects whether your video contains:
- **Spanish** (español) movie titles
- **English** movie titles
- **Mixed** Spanish and English content

Both OCR and Whisper transcription adapt to the detected language for optimal accuracy.

## How It Works

### 1. **Whisper Audio Detection**
- Analyzes first 30 seconds of audio
- Detects language with confidence scores
- Supports 99+ languages but optimized for Spanish/English
- Falls back to English if other language detected

### 2. **OCR Language Detection**
- Tests each frame with both English and Spanish models
- Compares confidence scores
- Selects language with higher accuracy
- Tracks primary language across all frames

### 3. **Language Reporting**
- Shows detected language in console output
- Includes language metadata in results
- Reports language mix in markdown output

## Usage

### Default (Auto-detect)

```bash
# Automatically detects Spanish or English
python main.py video.mp4 --oleada 1
```

### Force Specific Language

```bash
# Force English only
python main.py video.mp4 --oleada 1 --language en

# Force Spanish only
python main.py video.mp4 --oleada 1 --language es
```

### Disable Language Detection

```bash
# Use English only, no detection
python main.py video.mp4 --oleada 1 --no-language-detection
```

## Example Output

### Console Output

```
🔍 Detecting language...
   Detected: Spanish (es) - Confidence: 94.2%

🎤 Transcribing audio in Spanish: video.mp4
   Transcription complete. Language: es

🔍 Step 2/5: Running OCR on 30 frames...
   Primary OCR language detected: Spanish (spa)
   Found 5 potential titles via OCR
```

### Markdown Output

```markdown
# Oleada 01 - Movie List

**Total Movies:** 5
**Languages Detected:** Spanish

---

1. **El Padrino** (Confidence: 95%, Time: 00:15)
2. **Inception** (Confidence: 92%, Time: 01:23)
3. **Interestelar** (Confidence: 88%, Time: 02:45)
```

## Language Codes

| Code | Language | Tesseract | Whisper |
|------|----------|-----------|---------|
| `en` | English | ✅ | ✅ |
| `es` | Spanish | ✅ | ✅ |
| `eng` | English (OCR) | ✅ | - |
| `spa` | Spanish (OCR) | ✅ | - |

## Installing Spanish Language Data

### Tesseract Spanish Support

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract-lang
```

**Windows:**
Spanish data is included in the standard Tesseract installer.

### Verify Installation

```bash
# Check available languages
tesseract --list-langs

# Should show:
# List of available languages (3):
# eng
# osd
# spa
```

## Accuracy Improvements

### For Spanish Content

1. **Better OCR**: Spanish-specific character recognition (ñ, á, é, í, ó, ú, ü)
2. **Better Transcription**: Spanish phonetics and pronunciation
3. **Better Validation**: Spanish-aware string matching

### For Mixed Content

- Detects predominant language
- Uses appropriate models per segment
- Handles code-switching (Spanglish)

## Performance Impact

Language detection adds minimal overhead:

| Operation | Time Added |
|-----------|------------|
| Whisper detection | ~1-2 seconds |
| OCR per-frame detection | ~0.1 seconds |
| Total for 10-min video | ~5-10 seconds |

## Troubleshooting

### "Spanish language data not found"

Install Tesseract Spanish data:
```bash
sudo apt-get install tesseract-ocr-spa
```

### Poor Spanish OCR accuracy

1. Ensure Spanish data is installed
2. Use `--language es` to force Spanish
3. Check video quality and text clarity

### Wrong language detected

Force the correct language:
```bash
# Force Spanish
python main.py video.mp4 --oleada 1 --language es

# Force English
python main.py video.mp4 --oleada 1 --language en
```

## Advanced Usage

### Python API

```python
from src.movie_processor import MovieProcessor

# Auto-detect language
processor = MovieProcessor(
    whisper_model='base',
    auto_detect_language=True
)

# Force Spanish
processor = MovieProcessor(
    whisper_model='base',
    language='es',
    auto_detect_language=False
)

# Process video
result = processor.process_video('video.mp4', oleada_number=1)
print(f"Detected language: {result.get('language')}")
```

### Custom Language Detection

```python
from src.audio_transcriber import AudioTranscriber

transcriber = AudioTranscriber(model_size='base')
language = transcriber.detect_language('video.mp4')
print(f"Detected: {language}")
```

## Supported Languages (Future)

While optimized for Spanish/English, Whisper supports 99+ languages:

- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- And many more...

To add support for other languages, install the corresponding Tesseract language data and modify the language detection logic.

## Best Practices

1. **Let it auto-detect** for best results
2. **Force language** only if detection fails
3. **Install Spanish data** for Spanish content
4. **Check console output** to verify detection
5. **Review low-confidence** matches in interactive mode

---

**Questions?** Open an issue on GitHub!
