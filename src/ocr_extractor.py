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
    
    def __init__(self, lang: str = 'eng+spa', confidence_threshold: int = 30, auto_detect_language: bool = True):
        """
        Initialize OCR extractor.
        
        Args:
            lang: Tesseract language code (default: 'eng+spa' for English+Spanish)
            confidence_threshold: Minimum confidence to accept OCR result (0-100, lowered to 30)
            auto_detect_language: Try both English and Spanish, use best result
        """
        self.lang = lang
        self.confidence_threshold = confidence_threshold
        self.auto_detect_language = auto_detect_language
        self.detected_language = None
        
        # Configure Tesseract for better movie title recognition
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789áéíóúñÁÉÍÓÚÑ&: -'
        
        print(f"   OCR Config: confidence_threshold={confidence_threshold}, lang={lang}")
    
    def extract_text_from_frame(self, frame: np.ndarray, language: str = None) -> List[Dict]:
        """
        Extract text from a single frame with confidence scores.
        Uses multiple preprocessing techniques for better accuracy.
        
        Args:
            frame: Frame as numpy array (BGR format from OpenCV)
            language: Specific language to use ('eng', 'spa', or None for auto)
            
        Returns:
            List of dictionaries with 'text', 'confidence', and 'language' keys
        """
        # Generate multiple preprocessed versions
        preprocessed_images = self._create_preprocessing_variants(frame)
        
        lang_to_use = language if language else self.lang
        all_results = []
        
        # Try OCR on each preprocessed variant
        for idx, pil_image in enumerate(preprocessed_images):
            if self.auto_detect_language and not language:
                results_eng = self._extract_with_language(pil_image, 'eng')
                results_spa = self._extract_with_language(pil_image, 'spa')
                
                avg_conf_eng = sum([r['confidence'] for r in results_eng]) / len(results_eng) if results_eng else 0
                avg_conf_spa = sum([r['confidence'] for r in results_spa]) / len(results_spa) if results_spa else 0
                
                if avg_conf_spa > avg_conf_eng:
                    self.detected_language = 'spa'
                    all_results.extend(results_spa)
                else:
                    self.detected_language = 'eng'
                    all_results.extend(results_eng)
            else:
                results = self._extract_with_language(pil_image, lang_to_use)
                all_results.extend(results)
        
        # Deduplicate and return best results
        final_results = self._deduplicate_by_text(all_results)
        
        # Validate and filter results
        validated_results = [r for r in final_results if self._is_valid_movie_title(r['text'])]
        
        return validated_results
    
    def _create_preprocessing_variants(self, frame: np.ndarray) -> List[Image.Image]:
        """
        Create multiple preprocessing variants for robust OCR.
        
        Args:
            frame: Input frame
            
        Returns:
            List of PIL Images with different preprocessing
        """
        variants = []
        
        # Variant 1: Standard preprocessing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        if width < 800:
            scale_factor = 800 / width
            gray = cv2.resize(gray, (800, int(height * scale_factor)), interpolation=cv2.INTER_CUBIC)
        
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        variants.append(Image.fromarray(enhanced))
        
        # Variant 2: High contrast
        high_contrast = cv2.addWeighted(gray, 1.5, np.zeros(gray.shape, gray.dtype), 0, 0)
        high_contrast = cv2.fastNlMeansDenoising(high_contrast)
        _, thresh_high = cv2.threshold(high_contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(Image.fromarray(thresh_high))
        
        # Variant 3: Inverted (for light text on dark background)
        inverted = cv2.bitwise_not(gray)
        inverted_denoised = cv2.fastNlMeansDenoising(inverted)
        clahe_inv = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        inverted_enhanced = clahe_inv.apply(inverted_denoised)
        variants.append(Image.fromarray(inverted_enhanced))
        
        return variants
    
    def _is_valid_movie_title(self, text: str) -> bool:
        """
        Validate if extracted text looks like a valid movie title.
        
        Args:
            text: Extracted text
            
        Returns:
            True if valid, False otherwise
        """
        # Too short
        if len(text) < 2:
            return False
        
        # Too long
        if len(text) > 100:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-ZáéíóúñÁÉÍÓÚÑ]', text):
            return False
        
        # Reject if mostly numbers/symbols (less than 40% letters)
        alpha_count = sum(c.isalpha() or c in 'áéíóúñÁÉÍÓÚÑ' for c in text)
        if alpha_count / len(text) < 0.4:
            return False
        
        # Reject single characters
        if len(text.strip()) == 1:
            return False
        
        return True
    
    def _extract_with_language(self, pil_image: Image.Image, lang: str) -> List[Dict]:
        """
        Extract text using specific language with multiple configurations.
        
        Args:
            pil_image: PIL Image object
            lang: Language code
            
        Returns:
            List of text extraction results
        """
        all_results = []
        
        # Try multiple OCR configurations
        configs = [
            r'--oem 3 --psm 6',  # Single uniform block of text
            r'--oem 3 --psm 11', # Sparse text
            r'--oem 3 --psm 3',  # Fully automatic
        ]
        
        for config in configs:
            try:
                data = pytesseract.image_to_data(
                    pil_image, 
                    lang=lang, 
                    config=config,
                    output_type=pytesseract.Output.DICT
                )
                
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                    
                    if text and conf >= self.confidence_threshold and len(text) > 1:
                        # Clean up common OCR errors
                        cleaned_text = self._clean_ocr_text(text)
                        if cleaned_text:
                            all_results.append({
                                'text': cleaned_text,
                                'confidence': conf,
                                'language': lang,
                                'config': config
                            })
            except Exception as e:
                continue
        
        # Remove duplicates and return best confidence per text
        return self._deduplicate_by_text(all_results)
    
    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean up common OCR errors in movie titles.
        Uses generic pattern-based corrections.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove common OCR artifacts
        text = re.sub(r'[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s&:\-]', '', text)
        
        # Common character-level OCR substitutions (language-agnostic)
        char_substitutions = [
            (r'\b0\b', 'O'),      # Standalone 0 → O
            (r'\b1\b', 'I'),      # Standalone 1 → I  
            (r'\b5\b', 'S'),      # Standalone 5 → S
            (r'\b8\b', 'B'),      # Standalone 8 → B
            (r'rn', 'm'),          # Common: rn → m
            (r'vv', 'w'),          # Common: vv → w
            (r'\|', 'I'),          # Pipe → I
            (r'\[', 'I'),          # Bracket → I
            (r'\]', 'I'),          # Bracket → I
        ]
        
        for pattern, replacement in char_substitutions:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _deduplicate_by_text(self, results: List[Dict]) -> List[Dict]:
        """
        Remove duplicate text entries, keeping highest confidence.
        
        Args:
            results: List of OCR results
            
        Returns:
            Deduplicated results
        """
        text_map = {}
        
        for result in results:
            text_lower = result['text'].lower()
            if text_lower not in text_map or result['confidence'] > text_map[text_lower]['confidence']:
                text_map[text_lower] = result
        
        return list(text_map.values())
    
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
        
        print(f"   Processing {len(frames)} frames with enhanced OCR...")
        
        for idx, (frame, timestamp) in enumerate(frames):
            ocr_results = self.extract_text_from_frame(frame, language)
            
            if ocr_results:
                combined_text = ' '.join([r['text'] for r in ocr_results])
                avg_confidence = sum([r['confidence'] for r in ocr_results]) / len(ocr_results)
                
                frame_lang = ocr_results[0]['language'] if ocr_results else 'eng'
                detected_langs[frame_lang] = detected_langs.get(frame_lang, 0) + 1
                
                cleaned_title = self._clean_title(combined_text)
                if cleaned_title and self._is_valid_movie_title(cleaned_title):
                    movie_titles.append({
                        'title': cleaned_title,
                        'confidence': avg_confidence,
                        'timestamp': timestamp,
                        'source': 'ocr',
                        'language': frame_lang
                    })
                    print(f"      Frame {idx+1}: '{cleaned_title}' (conf: {avg_confidence:.0f}%)")
                else:
                    print(f"      Frame {idx+1}: No valid text detected")
            else:
                print(f"      Frame {idx+1}: No OCR results")
        
        primary_lang = max(detected_langs, key=detected_langs.get) if detected_langs else 'eng'
        lang_name = 'Spanish' if primary_lang == 'spa' else 'English'
        print(f"   Primary OCR language detected: {lang_name} ({primary_lang})")
        
        deduplicated = self._deduplicate_titles(movie_titles)
        print(f"   Final OCR titles: {len(deduplicated)} unique titles")
        
        return deduplicated
    
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
