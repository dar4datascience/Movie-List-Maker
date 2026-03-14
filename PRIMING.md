# 🎯 System Priming with Expected Movie Count

Improve accuracy by telling the system how many movies to expect.

## Why Prime the System?

When you know the number of movies in advance, the system can:

✅ **Adjust scene detection** - Fine-tune threshold to match expected count
✅ **Validate results** - Warn if count doesn't match
✅ **Filter duplicates** - Keep top N by confidence if too many found
✅ **Guide LLM** - Tell LLM exactly how many titles to extract
✅ **Catch errors** - Alert if movies are missing

## Usage

### Basic Processing with Expected Count

```bash
# You know there are 5 movies in the video
python main.py video.mp4 --oleada 1 --expected-movies 5
```

### Audio-Only Mode with Expected Count

```bash
# Tell LLM to extract exactly 5 titles
python main.py video.mp4 --oleada 1 --audio-only --expected-movies 5
```

### Batch Processing

```bash
# Process multiple videos, each with 5 movies
python main.py video1.mp4 video2.mp4 video3.mp4 --starting-oleada 1 --expected-movies 5
```

## How It Works

### 1. **Scene Detection Adjustment**

```
📹 Step 1/5: Detecting scene changes...
   Target: 5 movies
   Detected 10 scene segments
   ⚠️  Detected 10 scenes but expected 5
   Adjusting scene detection threshold...
   Adjusted to 5 scenes
```

**Logic:**
- Too many scenes → Increase threshold (less sensitive)
- Too few scenes → Decrease threshold (more sensitive)

### 2. **Result Validation**

```
✅ Step 5/5: Matching and validating titles...
   Expected: 5 movies, Found: 7 matches
   ⚠️  Found 2 extra matches
   Filtering to top 5 by confidence...
```

**Logic:**
- More than expected → Keep top N by confidence
- Less than expected → Warn user to check

### 3. **LLM Priming (Audio-Only)**

**Without priming:**
```
Your task:
1. Extract all movie titles mentioned in the transcription
```

**With priming:**
```
Expected number of movies: 5

Your task:
1. Extract all movie titles mentioned in the transcription
5. Extract exactly 5 movie titles
```

## Example Outputs

### Perfect Match

```bash
python main.py video.mp4 --oleada 1 --expected-movies 5 --whisper-model tiny
```

```
📹 Step 1/5: Detecting scene changes...
   Target: 5 movies
   Detected 5 scene segments ✅
   
✅ Step 5/5: Matching and validating titles...
   Expected: 5 movies, Found: 5 matches ✅
```

### Too Many Detected

```
📹 Step 1/5: Detecting scene changes...
   Target: 5 movies
   Detected 8 scene segments
   ⚠️  Detected 8 scenes but expected 5
   Adjusting scene detection threshold...
   Adjusted to 5 scenes
```

### Missing Movies

```
✅ Step 5/5: Matching and validating titles...
   Expected: 5 movies, Found: 3 matches
   ⚠️  Missing 2 movies
   Suggestion: Check if some scenes were missed or OCR/audio failed
   
   ⚠️  Final count: 3 (expected 5)
   Consider: --audio-only mode or manual review
```

## Best Practices

### When to Use

✅ **Use when:**
- You know the exact number of movies
- Video has consistent format (e.g., Oleada series)
- You want automatic validation
- Processing multiple similar videos

❌ **Don't use when:**
- Number of movies varies
- Exploratory processing
- Unknown video format

### Recommended Workflow

1. **First video:** Process without `--expected-movies` to discover count
2. **Subsequent videos:** Use `--expected-movies` for consistency
3. **Batch processing:** Apply same count to similar videos

### Combining with Other Flags

```bash
# Full optimization for 5-movie video
python main.py video.mp4 --oleada 1 \
  --expected-movies 5 \
  --whisper-model tiny \
  --language es \
  --frame-interval 30
```

## Troubleshooting

### "Detected X scenes but expected Y"

**Solution:** The threshold auto-adjusts, but if still wrong:
- Check if video has transitions/effects between movies
- Verify actual movie count in video
- Try `--audio-only` mode as fallback

### "Missing N movies"

**Possible causes:**
1. OCR failed on some covers
2. Audio unclear for some titles
3. Scene detection missed transitions

**Solutions:**
```bash
# Try audio-only mode
python main.py video.mp4 --oleada 1 --audio-only --expected-movies 5

# Lower frame interval for more samples
python main.py video.mp4 --oleada 1 --expected-movies 5 --frame-interval 15

# Use interactive mode to manually input
python main.py video.mp4 --oleada 1 --expected-movies 5
```

### "Found N extra matches"

**Solution:** System automatically keeps top N by confidence, but verify results.

## Advanced: Custom Thresholds

If auto-adjustment doesn't work, you can modify the thresholds in the code:

```python
# In movie_processor.py
if len(scenes) > self.expected_movie_count:
    scenes = self.video_processor.detect_scene_changes(video_path, threshold=40.0)  # Adjust this
else:
    scenes = self.video_processor.detect_scene_changes(video_path, threshold=20.0)  # Adjust this
```

## Summary

| Without Priming | With Priming |
|----------------|--------------|
| Accepts any scene count | Validates against expected |
| No threshold adjustment | Auto-adjusts detection |
| No result filtering | Filters to top N |
| Generic LLM prompt | Targeted LLM extraction |
| No warnings | Alerts on mismatches |

**Recommendation:** Always use `--expected-movies` when you know the count!

---

**Example for your 5-movie video:**
```bash
python main.py testo.mp4 --oleada 1 --whisper-model tiny --expected-movies 5
```
