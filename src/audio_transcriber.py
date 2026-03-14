import whisper
import os
import re
from typing import List, Dict
import warnings


class AudioTranscriber:
    """
    Transcribes audio from videos using OpenAI Whisper.
    Supports automatic language detection with preference for Spanish/English.
    """
    
    def __init__(self, model_size: str = 'base', auto_detect_language: bool = True):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
                       'base' is recommended for balance of speed and accuracy
            auto_detect_language: Automatically detect language (Spanish/English)
        """
        self.model_size = model_size
        self.auto_detect_language = auto_detect_language
        self.detected_language = None
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded successfully")
    
    def detect_language(self, video_path: str) -> str:
        """
        Detect language from audio (optimized for Spanish/English).
        
        Args:
            video_path: Path to video file
            
        Returns:
            Language code ('en' or 'es')
        """
        print("🔍 Detecting language...")
        
        audio = whisper.load_audio(video_path)
        audio = whisper.pad_or_trim(audio)
        
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        
        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        
        if detected_lang in ['en', 'es']:
            lang_name = 'English' if detected_lang == 'en' else 'Spanish'
            print(f"   Detected: {lang_name} ({detected_lang}) - Confidence: {probs[detected_lang]:.1%}")
            self.detected_language = detected_lang
            return detected_lang
        else:
            print(f"   Detected: {detected_lang} (Confidence: {probs[detected_lang]:.1%})")
            print(f"   Defaulting to English (most common alternative)")
            self.detected_language = 'en'
            return 'en'
    
    def transcribe_video(self, video_path: str, language: str = None) -> Dict:
        """
        Transcribe audio from video file with automatic language detection.
        
        Args:
            video_path: Path to video file
            language: Language code (e.g., 'en', 'es'). None for auto-detect
            
        Returns:
            Dictionary with transcription results including segments
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if language is None and self.auto_detect_language:
            language = self.detect_language(video_path)
        
        lang_name = {'en': 'English', 'es': 'Spanish'}.get(language, language)
        print(f"🎤 Transcribing audio in {lang_name}: {os.path.basename(video_path)}")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.model.transcribe(
                video_path,
                language=language,
                word_timestamps=True,
                verbose=False
            )
        
        actual_lang = result.get('language', 'unknown')
        print(f"   Transcription complete. Language: {actual_lang}")
        
        return result
    
    def extract_movie_titles_by_timestamps(self, video_path: str, ocr_timestamps: List[float], language: str = None, window_seconds: float = 3.0) -> List[Dict]:
        """
        Extract movie titles from audio based on OCR detection timestamps.
        Transcribes audio segments around each OCR detection time.
        
        Args:
            video_path: Path to video file
            ocr_timestamps: List of timestamps where OCR detected text
            language: Language code for transcription (auto-detected if None)
            window_seconds: Seconds before/after timestamp to transcribe
            
        Returns:
            List of dictionaries with 'title', 'confidence', 'timestamp', 'source', 'language'
        """
        if not ocr_timestamps:
            return self.extract_movie_titles(video_path, language)
        
        if language is None and self.auto_detect_language:
            language = self.detect_language(video_path)
        
        lang_name = {'en': 'English', 'es': 'Spanish'}.get(language, language)
        print(f"🎤 Transcribing audio segments in {lang_name} around {len(ocr_timestamps)} OCR detections")
        
        audio = whisper.load_audio(video_path)
        sample_rate = 16000
        
        movie_titles = []
        detected_lang = language or self.detected_language or 'en'
        
        for idx, timestamp in enumerate(ocr_timestamps):
            start_time = max(0, timestamp - window_seconds)
            end_time = timestamp + window_seconds
            
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            
            audio_segment = audio[start_sample:end_sample]
            
            if len(audio_segment) < sample_rate * 0.5:
                continue
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.model.transcribe(
                    audio_segment,
                    language=language,
                    fp16=False,
                    verbose=False
                )
            
            text = result.get('text', '').strip()
            
            if text:
                cleaned_text = self._clean_transcription(text)
                if cleaned_text:
                    movie_titles.append({
                        'title': cleaned_text,
                        'confidence': 0.95,
                        'timestamp': timestamp,
                        'source': 'audio',
                        'end_timestamp': timestamp + window_seconds,
                        'language': detected_lang
                    })
        
        print(f"   Extracted {len(movie_titles)} titles from audio segments")
        if movie_titles:
            print(f"   Sample titles: {', '.join([t['title'][:30] for t in movie_titles[:3]])}")
        
        return movie_titles
    
    def _clean_transcription(self, text: str) -> str:
        """
        Clean transcribed text to extract movie title.
        
        Args:
            text: Raw transcription
            
        Returns:
            Cleaned title
        """
        text = text.strip()
        
        text = re.sub(r'^(el|la|los|las|the|a|an)\s+', '', text, flags=re.IGNORECASE)
        
        text = re.sub(r'[^\w\s\-:&\']', '', text)
        text = ' '.join(text.split())
        
        return text if len(text) > 2 else ''
    
    def extract_movie_titles(self, video_path: str, language: str = None) -> List[Dict]:
        """
        Extract potential movie titles from audio transcription.
        Splits concatenated titles on commas and punctuation.
        
        Args:
            video_path: Path to video file
            language: Language code for transcription (auto-detected if None)
            
        Returns:
            List of dictionaries with 'title', 'confidence', 'timestamp', 'source', 'language'
        """
        result = self.transcribe_video(video_path, language)
        detected_lang = result.get('language', self.detected_language or 'en')
        
        movie_titles = []
        
        for segment in result.get('segments', []):
            text = segment['text'].strip()
            segment_start = segment['start']
            segment_end = segment['end']
            segment_duration = segment_end - segment_start
            
            if text:
                individual_titles = self._split_titles(text)
                
                if len(individual_titles) > 1:
                    time_per_title = segment_duration / len(individual_titles)
                    
                    for idx, title in enumerate(individual_titles):
                        title = title.strip()
                        if title and len(title) > 2:
                            timestamp = segment_start + (idx * time_per_title)
                            movie_titles.append({
                                'title': title,
                                'confidence': 1.0 - (segment.get('no_speech_prob', 0)),
                                'timestamp': timestamp,
                                'source': 'audio',
                                'end_timestamp': timestamp + time_per_title,
                                'language': detected_lang
                            })
                else:
                    movie_titles.append({
                        'title': text,
                        'confidence': 1.0 - (segment.get('no_speech_prob', 0)),
                        'timestamp': segment_start,
                        'source': 'audio',
                        'end_timestamp': segment_end,
                        'language': detected_lang
                    })
        
        return movie_titles
    
    def _split_titles(self, text: str) -> List[str]:
        """
        Split concatenated movie titles on commas, semicolons, and 'y'/'and'.
        
        Args:
            text: Concatenated text with multiple titles
            
        Returns:
            List of individual titles
        """
        text = text.strip()
        
        titles = re.split(r'[,;]|\by\b|\band\b', text, flags=re.IGNORECASE)
        
        cleaned_titles = []
        for title in titles:
            title = title.strip()
            title = re.sub(r'^(el|la|los|las|the|a|an)\s+', '', title, flags=re.IGNORECASE)
            
            if title and len(title) > 2:
                cleaned_titles.append(title)
        
        return cleaned_titles if cleaned_titles else [text]
    
    def get_full_transcription(self, video_path: str, language: str = None) -> str:
        """
        Get full text transcription of video audio.
        
        Args:
            video_path: Path to video file
            language: Language code
            
        Returns:
            Full transcription text
        """
        result = self.transcribe_video(video_path, language)
        return result.get('text', '').strip()
