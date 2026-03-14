import whisper
import os
from typing import List, Dict
import warnings


class AudioTranscriber:
    """
    Transcribes audio from videos using OpenAI Whisper.
    """
    
    def __init__(self, model_size: str = 'base'):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
                       'base' is recommended for balance of speed and accuracy
        """
        self.model_size = model_size
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded successfully")
    
    def transcribe_video(self, video_path: str, language: str = None) -> Dict:
        """
        Transcribe audio from video file.
        
        Args:
            video_path: Path to video file
            language: Language code (e.g., 'en', 'es'). None for auto-detect
            
        Returns:
            Dictionary with transcription results including segments
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        print(f"Transcribing audio from: {video_path}")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.model.transcribe(
                video_path,
                language=language,
                word_timestamps=True,
                verbose=False
            )
        
        print(f"Transcription complete. Detected language: {result.get('language', 'unknown')}")
        
        return result
    
    def extract_movie_titles(self, video_path: str, language: str = None) -> List[Dict]:
        """
        Extract potential movie titles from audio transcription.
        
        Args:
            video_path: Path to video file
            language: Language code for transcription
            
        Returns:
            List of dictionaries with 'title', 'confidence', 'timestamp', 'source'
        """
        result = self.transcribe_video(video_path, language)
        
        movie_titles = []
        
        for segment in result.get('segments', []):
            text = segment['text'].strip()
            
            if text:
                movie_titles.append({
                    'title': text,
                    'confidence': segment.get('no_speech_prob', 0) * 100,
                    'timestamp': segment['start'],
                    'source': 'audio',
                    'end_timestamp': segment['end']
                })
        
        return movie_titles
    
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
