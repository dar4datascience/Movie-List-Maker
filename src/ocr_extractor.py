import pytesseract
from PIL import Image
import numpy as np
import re
from typing import List, Dict
import cv2


class OCRExtractor:
    """
    Extracts text from video frames using Tesseract OCR.
    Supports Spanish and English with automatic language detection.
    """
    
    def __init__(self, lang: str = 'eng+spa', confidence_threshold: int = 60, auto_detect_language: bool = True):
        """
        Initialize OCR extractor.
        
        Args:
            lang: Tesseract language code (default: 'eng+spa' for English+Spanish)
            confidence_threshold: Minimum confidence to accept OCR result (0-100)
            auto_detect_language: Try both English and Spanish, use best result
        """
        self.lang = lang
        self.confidence_threshold = confidence_threshold
        self.auto_detect_language = auto_detect_language
        self.detected_language = None
    
    def extract_text_from_frame(self, frame: np.ndarray, language: str = None) -> List[Dict]:
        """
        Extract text from a single frame with confidence scores.
        Supports Spanish and English language detection.
        
        Args:
            frame: Frame as numpy array (BGR format from OpenCV)
            language: Specific language to use ('eng', 'spa', or None for auto)
            
        Returns:
            List of dictionaries with 'text', 'confidence', and 'language' keys
        """
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        lang_to_use = language if language else self.lang
        
        if self.auto_detect_language and not language:
            results_eng = self._extract_with_language(pil_image, 'eng')
            results_spa = self._extract_with_language(pil_image, 'spa')
            
            avg_conf_eng = sum([r['confidence'] for r in results_eng]) / len(results_eng) if results_eng else 0
            avg_conf_spa = sum([r['confidence'] for r in results_spa]) / len(results_spa) if results_spa else 0
            
            if avg_conf_spa > avg_conf_eng:
                self.detected_language = 'spa'
                return results_spa
            else:
                self.detected_language = 'eng'
                return results_eng
        else:
            return self._extract_with_language(pil_image, lang_to_use)
    
    def _extract_with_language(self, pil_image: Image.Image, lang: str) -> List[Dict]:
        """
        Extract text using specific language.
        
        Args:
            pil_image: PIL Image object
            lang: Language code
            
        Returns:
            List of text extraction results
        """
        data = pytesseract.image_to_data(pil_image, lang=lang, output_type=pytesseract.Output.DICT)
        
        results = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
            
            if text and conf >= self.confidence_threshold:
                results.append({
                    'text': text,
                    'confidence': conf,
                    'language': lang
                })
        
        return results
    
    def extract_movie_titles(self, frames: List[tuple], language: str = None) -> List[Dict]:
        """
        Extract potential movie titles from multiple frames.
        
        Args:
            frames: List of tuples (frame_array, timestamp)
            language: Specific language to use (None for auto-detect)
            
        Returns:
            List of dictionaries with 'title', 'confidence', 'timestamp', 'language'
        """
        movie_titles = []
        detected_langs = {'eng': 0, 'spa': 0}
        
        for frame, timestamp in frames:
            ocr_results = self.extract_text_from_frame(frame, language)
            
            combined_text = ' '.join([r['text'] for r in ocr_results])
            avg_confidence = sum([r['confidence'] for r in ocr_results]) / len(ocr_results) if ocr_results else 0
            
            frame_lang = ocr_results[0]['language'] if ocr_results else 'eng'
            detected_langs[frame_lang] = detected_langs.get(frame_lang, 0) + 1
            
            if combined_text:
                cleaned_title = self._clean_title(combined_text)
                if cleaned_title:
                    movie_titles.append({
                        'title': cleaned_title,
                        'confidence': avg_confidence,
                        'timestamp': timestamp,
                        'source': 'ocr',
                        'language': frame_lang
                    })
        
        primary_lang = max(detected_langs, key=detected_langs.get) if detected_langs else 'eng'
        lang_name = 'Spanish' if primary_lang == 'spa' else 'English'
        print(f"   Primary OCR language detected: {lang_name} ({primary_lang})")
        
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
