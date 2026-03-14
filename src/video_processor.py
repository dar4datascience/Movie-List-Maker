import cv2
import os
from pathlib import Path
from typing import List, Tuple
import numpy as np


class VideoProcessor:
    """
    Handles video frame extraction using OpenCV.
    Optimized for lightweight processing with configurable frame sampling.
    """
    
    def __init__(self, frame_interval: int = 30):
        """
        Initialize video processor.
        
        Args:
            frame_interval: Extract one frame every N frames (default: 30, ~1 frame/sec at 30fps)
        """
        self.frame_interval = frame_interval
    
    def extract_frames(self, video_path: str, output_dir: str = None) -> List[Tuple[np.ndarray, float]]:
        """
        Extract frames from video at regular intervals.
        
        Args:
            video_path: Path to input video file
            output_dir: Optional directory to save extracted frames
            
        Returns:
            List of tuples (frame_array, timestamp_seconds)
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames = []
        frame_count = 0
        
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"Processing video: {video_path}")
        print(f"FPS: {fps}, Total frames: {total_frames}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % self.frame_interval == 0:
                timestamp = frame_count / fps
                frames.append((frame, timestamp))
                
                if output_dir:
                    frame_filename = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                    cv2.imwrite(frame_filename, frame)
            
            frame_count += 1
        
        cap.release()
        print(f"Extracted {len(frames)} frames from {total_frames} total frames")
        
        return frames
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for better OCR accuracy.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Preprocessed frame
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        denoised = cv2.fastNlMeansDenoising(gray)
        
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """
        Get video duration in seconds.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        return frame_count / fps if fps > 0 else 0
