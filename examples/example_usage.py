#!/usr/bin/env python3
"""
Example usage scripts for Movie List Maker
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.movie_processor import MovieProcessor


def example_basic():
    """Basic usage: Process single video"""
    print("Example 1: Basic Usage\n")
    
    processor = MovieProcessor(
        whisper_model='base',
        frame_interval=30,
        confidence_threshold=0.90
    )
    
    result = processor.process_video(
        video_path='path/to/video.mp4',
        oleada_number=1,
        interactive=True
    )
    
    print(f"Processed {result['total_movies']} movies")


def example_batch():
    """Batch processing: Multiple videos"""
    print("Example 2: Batch Processing\n")
    
    processor = MovieProcessor(whisper_model='tiny')
    
    videos = [
        'path/to/video1.mp4',
        'path/to/video2.mp4',
        'path/to/video3.mp4'
    ]
    
    results = processor.process_multiple_videos(
        videos,
        starting_oleada=1,
        interactive=False
    )
    
    processor.generate_quarto_website(results)


def example_fast():
    """Fast processing: Optimized for speed"""
    print("Example 3: Fast Processing\n")
    
    processor = MovieProcessor(
        whisper_model='tiny',
        frame_interval=60,
        confidence_threshold=0.80
    )
    
    result = processor.process_video(
        video_path='path/to/video.mp4',
        oleada_number=1,
        interactive=False
    )


def example_high_accuracy():
    """High accuracy: Optimized for quality"""
    print("Example 4: High Accuracy Processing\n")
    
    processor = MovieProcessor(
        whisper_model='small',
        frame_interval=15,
        confidence_threshold=0.95
    )
    
    result = processor.process_video(
        video_path='path/to/video.mp4',
        oleada_number=1,
        interactive=True,
        save_frames=True
    )


if __name__ == '__main__':
    print("Movie List Maker - Example Usage\n")
    print("=" * 60)
    print("\nAvailable examples:")
    print("1. Basic usage")
    print("2. Batch processing")
    print("3. Fast processing")
    print("4. High accuracy processing")
    print("\nUncomment the example you want to run in this file.")
    print("=" * 60)
    
    # Uncomment one of these to run:
    # example_basic()
    # example_batch()
    # example_fast()
    # example_high_accuracy()
