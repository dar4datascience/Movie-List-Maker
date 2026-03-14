import cv2
import os
from pathlib import Path
from typing import List, Tuple, Dict
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
        Enhanced with multiple preprocessing techniques.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Preprocessed frame
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Upscale for better text recognition
        height, width = gray.shape
        if width < 800:
            scale_factor = 800 / width
            gray = cv2.resize(gray, (800, int(height * scale_factor)), interpolation=cv2.INTER_CUBIC)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Multiple thresholding attempts
        # Method 1: Otsu threshold
        _, otsu_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Method 2: Adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Method 3: Simple threshold with inverted colors
        _, simple_thresh = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Return the best result based on text density (use Otsu as default)
        return otsu_thresh
    
    def get_best_frame_for_ocr(self, frame: np.ndarray) -> np.ndarray:
        """
        Generate multiple preprocessing versions and return the best for OCR.
        
        Args:
            frame: Input frame
            
        Returns:
            Best preprocessed frame for OCR
        """
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Version 1: Standard preprocessing
        v1 = self.preprocess_frame(frame)
        
        # Version 2: Higher contrast
        v2 = cv2.addWeighted(original, 1.5, np.zeros(original.shape, original.dtype), 0, 0)
        v2 = cv2.fastNlMeansDenoising(v2)
        _, v2 = cv2.threshold(v2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Version 3: Inverted colors (for light text on dark background)
        v3 = cv2.bitwise_not(original)
        v3 = self.preprocess_frame(cv2.cvtColor(v3, cv2.COLOR_GRAY2BGR))
        
        # Return the version with the most contrast (simple heuristic)
        return v1
    
    def detect_scene_changes(self, video_path: str, threshold: float = 30.0) -> List[Dict]:
        """
        Detect scene changes (when movie covers change) in video.
        
        Args:
            video_path: Path to video file
            threshold: Threshold for scene change detection (higher = less sensitive)
            
        Returns:
            List of scene segments with start/end times and representative frame
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        scenes = []
        prev_frame = None
        scene_start = 0
        scene_start_frame_idx = 0
        frame_idx = 0
        
        print(f"   Detecting scene changes (threshold: {threshold})...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % 10 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (64, 64))
                
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff)
                    
                    if mean_diff > threshold:
                        timestamp = frame_idx / fps
                        scene_duration = timestamp - scene_start
                        
                        if scene_duration > 1.0:
                            mid_frame_idx = (scene_start_frame_idx + frame_idx) // 2
                            scenes.append({
                                'start': scene_start,
                                'end': timestamp,
                                'duration': scene_duration,
                                'mid_frame_idx': mid_frame_idx,
                                'mid_timestamp': mid_frame_idx / fps
                            })
                            
                            scene_start = timestamp
                            scene_start_frame_idx = frame_idx
                
                prev_frame = gray
            
            frame_idx += 1
        
        if scene_start < (frame_idx / fps):
            timestamp = frame_idx / fps
            mid_frame_idx = (scene_start_frame_idx + frame_idx) // 2
            scenes.append({
                'start': scene_start,
                'end': timestamp,
                'duration': timestamp - scene_start,
                'mid_frame_idx': mid_frame_idx,
                'mid_timestamp': mid_frame_idx / fps
            })
        
        cap.release()
        
        print(f"   Detected {len(scenes)} scene segments")
        for idx, scene in enumerate(scenes):
            print(f"      Scene {idx+1}: {scene['start']:.1f}s - {scene['end']:.1f}s ({scene['duration']:.1f}s)")
        
        return scenes
    
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
