#!/usr/bin/env python3
"""
Movie List Maker - CLI Interface

Process videos of movie covers with spoken titles to extract and generate
movie lists with Quarto websites.
"""

import argparse
import sys
import os
from pathlib import Path

from src.movie_processor import MovieProcessor


def main():
    parser = argparse.ArgumentParser(
        description='Process movie cover videos and generate Quarto websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single video
  python main.py video.mp4 --oleada 1
  
  # Process multiple videos
  python main.py video1.mp4 video2.mp4 video3.mp4 --starting-oleada 1
  
  # Non-interactive mode (auto-accept all matches)
  python main.py video.mp4 --oleada 1 --no-interactive
  
  # Use smaller Whisper model for faster processing
  python main.py video.mp4 --oleada 1 --whisper-model tiny
  
  # Save extracted frames for debugging
  python main.py video.mp4 --oleada 1 --save-frames
        """
    )
    
    parser.add_argument(
        'videos',
        nargs='+',
        help='Path(s) to video file(s) to process'
    )
    
    parser.add_argument(
        '--oleada',
        type=int,
        help='Oleada number (for single video)'
    )
    
    parser.add_argument(
        '--starting-oleada',
        type=int,
        default=1,
        help='Starting oleada number for multiple videos (default: 1)'
    )
    
    parser.add_argument(
        '--frame-interval',
        type=int,
        default=30,
        help='Extract one frame every N frames (default: 30)'
    )
    
    parser.add_argument(
        '--whisper-model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='base',
        help='Whisper model size (default: base). Tiny is fastest, large is most accurate.'
    )
    
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.90,
        help='Confidence threshold for auto-accepting matches (0-1, default: 0.90)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for intermediate files (default: output)'
    )
    
    parser.add_argument(
        '--quarto-dir',
        default='quarto_site',
        help='Quarto project directory (default: quarto_site)'
    )
    
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Disable interactive prompts for low-confidence matches'
    )
    
    parser.add_argument(
        '--save-frames',
        action='store_true',
        help='Save extracted frames to disk for debugging'
    )
    
    parser.add_argument(
        '--skip-quarto',
        action='store_true',
        help='Skip Quarto website generation'
    )
    
    args = parser.parse_args()
    
    for video_path in args.videos:
        if not os.path.exists(video_path):
            print(f"❌ Error: Video file not found: {video_path}")
            sys.exit(1)
    
    print("\n" + "="*70)
    print("🎬 Movie List Maker")
    print("="*70)
    print(f"Videos to process: {len(args.videos)}")
    print(f"Whisper model: {args.whisper_model}")
    print(f"Frame interval: {args.frame_interval}")
    print(f"Confidence threshold: {args.confidence_threshold * 100}%")
    print(f"Interactive mode: {'No' if args.no_interactive else 'Yes'}")
    print("="*70 + "\n")
    
    processor = MovieProcessor(
        frame_interval=args.frame_interval,
        whisper_model=args.whisper_model,
        confidence_threshold=args.confidence_threshold,
        output_dir=args.output_dir,
        quarto_dir=args.quarto_dir
    )
    
    if len(args.videos) == 1 and args.oleada:
        results = [processor.process_video(
            args.videos[0],
            args.oleada,
            interactive=not args.no_interactive,
            save_frames=args.save_frames
        )]
    else:
        results = processor.process_multiple_videos(
            args.videos,
            starting_oleada=args.starting_oleada,
            interactive=not args.no_interactive
        )
    
    if not args.skip_quarto:
        processor.generate_quarto_website(results)
    
    print("\n" + "="*70)
    print("🎉 All processing complete!")
    print("="*70)
    print(f"\nProcessed {len(results)} video(s)")
    for result in results:
        print(f"  - Oleada {result['oleada_number']:02d}: {result['total_movies']} movies")
    
    if not args.skip_quarto:
        print(f"\n📁 Quarto website: {args.quarto_dir}")
        print(f"📁 Output files: {args.output_dir}")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
