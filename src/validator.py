from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple
import re


class MovieValidator:
    """
    Validates and matches movie titles from OCR and audio sources.
    Implements confidence scoring and user prompting for low-confidence matches.
    """
    
    def __init__(self, confidence_threshold: float = 0.90):
        """
        Initialize validator.
        
        Args:
            confidence_threshold: Minimum similarity score (0-1) to auto-accept match
        """
        self.confidence_threshold = confidence_threshold
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.
        
        Args:
            text1: First string
            text2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        text1_clean = self._normalize_text(text1)
        text2_clean = self._normalize_text(text2)
        
        return SequenceMatcher(None, text1_clean, text2_clean).ratio()
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def match_titles(self, ocr_titles: List[Dict], audio_titles: List[Dict]) -> List[Dict]:
        """
        Match OCR and audio titles, calculating confidence scores.
        
        Args:
            ocr_titles: List of OCR-extracted titles
            audio_titles: List of audio-transcribed titles
            
        Returns:
            List of matched titles with confidence scores
        """
        matched_titles = []
        used_audio_indices = set()
        
        for ocr_title in ocr_titles:
            best_match = None
            best_similarity = 0
            best_audio_idx = -1
            
            for idx, audio_title in enumerate(audio_titles):
                if idx in used_audio_indices:
                    continue
                
                similarity = self.calculate_similarity(
                    ocr_title['title'],
                    audio_title['title']
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = audio_title
                    best_audio_idx = idx
            
            if best_match and best_similarity >= 0.5:
                used_audio_indices.add(best_audio_idx)
                
                matched_titles.append({
                    'ocr_title': ocr_title['title'],
                    'audio_title': best_match['title'],
                    'final_title': best_match['title'] if best_similarity >= 0.7 else ocr_title['title'],
                    'confidence': best_similarity,
                    'timestamp': ocr_title.get('timestamp', best_match.get('timestamp', 0)),
                    'needs_review': best_similarity < self.confidence_threshold
                })
            else:
                matched_titles.append({
                    'ocr_title': ocr_title['title'],
                    'audio_title': None,
                    'final_title': ocr_title['title'],
                    'confidence': ocr_title.get('confidence', 0) / 100,
                    'timestamp': ocr_title.get('timestamp', 0),
                    'needs_review': True
                })
        
        for idx, audio_title in enumerate(audio_titles):
            if idx not in used_audio_indices:
                matched_titles.append({
                    'ocr_title': None,
                    'audio_title': audio_title['title'],
                    'final_title': audio_title['title'],
                    'confidence': 1.0 - audio_title.get('confidence', 0) / 100,
                    'timestamp': audio_title.get('timestamp', 0),
                    'needs_review': True
                })
        
        matched_titles.sort(key=lambda x: x['timestamp'])
        
        return matched_titles
    
    def prompt_user_selection(self, ocr_title: str, audio_title: str, confidence: float) -> str:
        """
        Prompt user to select correct title when confidence is low.
        
        Args:
            ocr_title: Title from OCR
            audio_title: Title from audio
            confidence: Confidence score (0-1)
            
        Returns:
            Selected title
        """
        print("\n" + "="*60)
        print(f"⚠️  Low confidence match detected ({confidence*100:.1f}%)")
        print("="*60)
        print(f"1. OCR detected:   {ocr_title}")
        print(f"2. Audio detected: {audio_title}")
        print(f"3. Enter custom title")
        print("="*60)
        
        while True:
            choice = input("Select option (1/2/3): ").strip()
            
            if choice == '1':
                return ocr_title
            elif choice == '2':
                return audio_title
            elif choice == '3':
                custom = input("Enter correct title: ").strip()
                if custom:
                    return custom
                print("Title cannot be empty. Please try again.")
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def validate_and_resolve(self, matched_titles: List[Dict], interactive: bool = True) -> List[Dict]:
        """
        Validate matched titles and resolve conflicts.
        
        Args:
            matched_titles: List of matched title dictionaries
            interactive: Whether to prompt user for low-confidence matches
            
        Returns:
            List of validated titles
        """
        validated_titles = []
        
        for match in matched_titles:
            if match['needs_review'] and interactive:
                if match['ocr_title'] and match['audio_title']:
                    selected = self.prompt_user_selection(
                        match['ocr_title'],
                        match['audio_title'],
                        match['confidence']
                    )
                    match['final_title'] = selected
                    match['user_selected'] = True
                elif not match['audio_title']:
                    print(f"\n⚠️  Only OCR detected: {match['ocr_title']}")
                    confirm = input("Accept this title? (y/n): ").strip().lower()
                    if confirm != 'y':
                        custom = input("Enter correct title: ").strip()
                        if custom:
                            match['final_title'] = custom
                            match['user_selected'] = True
                elif not match['ocr_title']:
                    print(f"\n⚠️  Only audio detected: {match['audio_title']}")
                    confirm = input("Accept this title? (y/n): ").strip().lower()
                    if confirm != 'y':
                        custom = input("Enter correct title: ").strip()
                        if custom:
                            match['final_title'] = custom
                            match['user_selected'] = True
            
            validated_titles.append(match)
        
        return validated_titles
