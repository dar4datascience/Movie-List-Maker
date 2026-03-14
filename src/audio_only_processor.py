import whisper
import os
import json
from typing import List, Dict
import warnings


class AudioOnlyProcessor:
    """
    Process audio-only mode: extract full transcription and use LLM to parse movie titles.
    """
    
    def __init__(self, model_size: str = 'base'):
        """
        Initialize audio-only processor.
        
        Args:
            model_size: Whisper model size
        """
        self.model_size = model_size
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded successfully")
    
    def extract_full_transcription(self, video_path: str, language: str = None) -> str:
        """
        Extract full audio transcription from video.
        
        Args:
            video_path: Path to video file
            language: Language code (auto-detect if None)
            
        Returns:
            Full transcription text
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        print(f"\n🎤 Transcribing full audio from: {os.path.basename(video_path)}")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.model.transcribe(
                video_path,
                language=language,
                verbose=False
            )
        
        detected_lang = result.get('language', 'unknown')
        text = result.get('text', '').strip()
        
        print(f"   Language detected: {detected_lang}")
        print(f"   Transcription length: {len(text)} characters")
        
        return text
    
    def generate_llm_prompt(self, transcription: str, language: str = 'en', expected_count: int = None) -> str:
        """
        Generate prompt for LLM to extract movie and TV show titles.
        
        Args:
            transcription: Full audio transcription
            language: Language of transcription
            expected_count: Expected number of titles (helps LLM)
            
        Returns:
            Formatted prompt for LLM
        """
        lang_instruction = {
            'en': 'The transcription is in English.',
            'es': 'The transcription is in Spanish (español).'
        }.get(language, 'The transcription may be in English or Spanish.')
        
        count_instruction = f"\nExpected number of titles: {expected_count}" if expected_count else ""
        task_5 = f"\n5. Extract exactly {expected_count} titles" if expected_count else ""
        
        # Language-specific error corrections
        error_corrections = {
            'es': '''
Specific error corrections for Spanish transcription:
- "Jóbul" → "Hubble telescope" (Jóbul is Hubble in Spanish)
- "chicheniza" → "Chichén Itzá" (famous Mayan site)
- "Si es Ayma y Ami" → "Sesame Street" (Plaza Sésamo)
- "Gritos temuerte libertad" → "Gritos de muerte y libertad" (Mexican film)
- "El encanto de la guila" → "El encanto del águila" (Mexican film)
- "temuerte" → "muerte" (remove extra 'te')
- "number once" → "number one" (English correction)
- "Ley de l'orden" → "Ley y orden" (Law & Order)
- "Wilma" → "Wanda" (possible Marvel reference)''',
            'en': '''
Common transcription errors to fix:
- Remove extra letters like "temuerte" → "muerte"
- Fix number words like "number once" → "number one"
- Correct location names and famous references'''
        }.get(language, '')
        
        prompt = f"""You are a movie and TV show title extraction assistant. Below is an audio transcription from a video showing movie/TV covers with spoken titles.

{lang_instruction}{count_instruction}

Your task:
1. Extract ALL titles mentioned (movies, TV shows, documentaries)
2. Include season information when mentioned (e.g., "primera temporada", "Temporada 4")
3. Return them as a numbered list
4. Clean up transcription errors using the specific corrections below
5. Preserve the original language of the titles
6. Format titles properly (capitalize correctly){task_5}

{error_corrections}

Transcription:
{transcription}

Please provide a numbered list of titles (one per line), including both movies and TV shows with their seasons when mentioned:"""
        
        return prompt
    
    def save_for_llm_processing(self, transcription: str, output_path: str, language: str = 'en', expected_count: int = None):
        """
        Save transcription and prompt for LLM processing.
        
        Args:
            transcription: Full transcription
            output_path: Path to save output
            language: Detected language
        """
        prompt = self.generate_llm_prompt(transcription, language, expected_count)
        
        output_data = {
            'transcription': transcription,
            'language': language,
            'llm_prompt': prompt,
            'instructions': 'Copy the llm_prompt to your local LLM (e.g., Ollama, LM Studio) to extract movie titles.'
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        prompt_file = output_path.replace('.json', '_prompt.txt')
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"\n✅ Audio transcription saved to: {output_path}")
        print(f"✅ LLM prompt saved to: {prompt_file}")
        print(f"\n📋 Next steps:")
        print(f"   1. Copy the prompt from: {prompt_file}")
        print(f"   2. Paste it into your local LLM (Ollama, LM Studio, etc.)")
        print(f"   3. The LLM will return a numbered list of movie titles")
        
        return output_path
