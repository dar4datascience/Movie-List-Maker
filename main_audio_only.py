#!/usr/bin/env python3
"""
Movie List Maker - Audio-Only Mode

Extract audio transcription and generate LLM prompt for movie title extraction.
"""

import argparse
import sys
import os

from src.audio_only_processor import AudioOnlyProcessor


def main():
    parser = argparse.ArgumentParser(
        description='Extract audio transcription for LLM processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract audio and generate LLM prompt
  python main_audio_only.py video.mp4 --output audio_output.json
  
  # Force Spanish language
  python main_audio_only.py video.mp4 --language es --output audio_output.json
  
  # Use faster Whisper model
  python main_audio_only.py video.mp4 --whisper-model tiny --output audio_output.json
        """
    )
    
    parser.add_argument(
        'video',
        help='Path to video file to process'
    )
    
    parser.add_argument(
        '--output',
        default='audio_transcription.json',
        help='Output file for transcription and LLM prompt (default: audio_transcription.json)'
    )
    
    parser.add_argument(
        '--whisper-model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='base',
        help='Whisper model size (default: base)'
    )
    
    parser.add_argument(
        '--language',
        choices=['auto', 'en', 'es'],
        default='auto',
        help='Language for transcription (default: auto-detect)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"❌ Error: Video file not found: {args.video}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🎤 Movie List Maker - Audio-Only Mode")
    print("="*70)
    print(f"Video: {args.video}")
    print(f"Whisper model: {args.whisper_model}")
    print(f"Language: {args.language}")
    print("="*70)
    
    processor = AudioOnlyProcessor(model_size=args.whisper_model)
    
    language = None if args.language == 'auto' else args.language
    transcription = processor.extract_full_transcription(args.video, language=language)
    
    detected_lang = 'es' if any(word in transcription.lower() for word in ['el', 'la', 'los', 'las']) else 'en'
    
    output_path = processor.save_for_llm_processing(
        transcription,
        args.output,
        language=detected_lang
    )
    
    print("\n" + "="*70)
    print("✨ Audio extraction complete!")
    print("="*70)
    print(f"\n📄 Transcription preview:")
    print(f"   {transcription[:200]}...")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
