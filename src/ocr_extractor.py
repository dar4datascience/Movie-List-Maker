import pytesseract
from PIL import Image
import numpy as np
import re
from typing import List, Dict
import cv2


class OCRExtractor:
    """
    Extracts text from video frames using Tesseract OCR.
    """
    
    def __init__(self, lang: str = 'eng', confidence_threshold: int = 60):
        """
        Initialize OCR extractor.
        
        Args:
            lang: Tesseract language code (default: 'eng')
            confidence_threshold: Minimum confidence to accept OCR result (0-100)
        """
        self.lang = lang
        self.confidence_threshold = confidence_threshold
    
    def extract_text_from_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Extract text from a single frame with confidence scores.
        
        Args:
            frame: Frame as numpy array (BGR format from OpenCV)
            
        Returns:
            List of dictionaries with 'text' and 'confidence' keys
        """
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        data = pytesseract.image_to_data(pil_image, lang=self.lang, output_type=pytesseract.Output.DICT)
        
        results = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
            
            if text and conf >= self.confidence_threshold:
                results.append({
                    'text': text,
                    'confidence': conf
                })
        
        return results
    
    def extract_movie_titles(self, frames: List[tuple]) -> List[Dict]:
        """
        Extract potential movie titles from multiple frames.
        
        Args:
            frames: List of tuples (frame_array, timestamp)
            
        Returns:
            List of dictionaries with 'title', 'confidence', 'timestamp'
        """
        movie_titles = []
        
        for frame, timestamp in frames:
            ocr_results = self.extract_text_from_frame(frame)
            
            combined_text = ' '.join([r['text'] for r in ocr_results])
            avg_confidence = sum([r['confidence'] for r in ocr_results]) / len(ocr_results) if ocr_results else 0
            
            if combined_text:
                cleaned_title = self._clean_title(combined_text)
                if cleaned_title:
                    movie_titles.append({
                        'title': cleaned_title,
                        'confidence': avg_confidence,
                        'timestamp': timestamp,
                        'source': 'ocr'
                    })
        
        return self._deduplicate_titles(movie_titles)
    
    def _clean_title(self, text: str) -> str:
        """
        Clean and normalize extracted text to get movie title.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned title string
        """
        text = re.sub(r'[^\w\s\-:&\']', '', text)
        text = ' '.join(text.split())
        
        if len(text) < 2 or len(text) > 100:
            return ""
        
        return text
    
    def _deduplicate_titles(self, titles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate titles, keeping the one with highest confidence.
        
        Args:
            titles: List of title dictionaries
            
        Returns:
            Deduplicated list
        """
        unique_titles = {}
        
        for title_data in titles:
            title = title_data['title'].lower()
            
            if title not in unique_titles or title_data['confidence'] > unique_titles[title]['confidence']:
                unique_titles[title] = title_data
        
        return list(unique_titles.values())
