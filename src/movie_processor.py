import os
import cv2
from typing import List, Dict, Optional
from pathlib import Path

from .video_processor import VideoProcessor
from .ocr_extractor import OCRExtractor
from .audio_transcriber import AudioTranscriber
from .validator import MovieValidator
from .markdown_generator import MarkdownGenerator
from .quarto_generator import QuartoGenerator
from .audio_only_processor import AudioOnlyProcessor


class MovieProcessor:
    """
    Main orchestrator for processing movie cover videos.
    Coordinates all components to extract, validate, and generate output.
    """
    
    def __init__(
        self,
        frame_interval: int = 30,
        whisper_model: str = 'base',
        confidence_threshold: float = 0.90,
        output_dir: str = 'output',
        quarto_dir: str = 'quarto_site',
        language: str = None,
        auto_detect_language: bool = True
    ):
        """
        Initialize movie processor with all components.
        
        Args:
            frame_interval: Frames between extractions (default: 30)
            whisper_model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            confidence_threshold: Minimum confidence for auto-accept (0-1)
            output_dir: Directory for intermediate outputs
            quarto_dir: Directory for Quarto website
            language: Specific language ('en', 'es', or None for auto-detect)
            auto_detect_language: Enable automatic language detection
        """
        self.video_processor = VideoProcessor(frame_interval=frame_interval)
        self.ocr_extractor = OCRExtractor(auto_detect_language=auto_detect_language)
        self.audio_transcriber = AudioTranscriber(
            model_size=whisper_model,
            auto_detect_language=auto_detect_language
        )
        self.validator = MovieValidator(confidence_threshold=confidence_threshold)
        self.markdown_generator = MarkdownGenerator(output_dir=output_dir)
        self.quarto_generator = QuartoGenerator(project_dir=quarto_dir)
        
        self.output_dir = output_dir
        self.quarto_dir = quarto_dir
        self.language = language
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def process_video(
        self,
        video_path: str,
        oleada_number: int,
        interactive: bool = True,
        save_frames: bool = False
    ) -> Dict:
        """
        Process a single video to extract movie list.
        
        Args:
            video_path: Path to video file
            oleada_number: Oleada edition number
            interactive: Whether to prompt user for low-confidence matches
            save_frames: Whether to save extracted frames to disk
            
        Returns:
            Dictionary with processing results
        """
        print("\n" + "="*70)
        print(f"🎬 Processing Oleada {oleada_number:02d}: {os.path.basename(video_path)}")
        print("="*70 + "\n")
        
        frames_dir = None
        if save_frames:
            frames_dir = os.path.join(self.output_dir, f'oleada_{oleada_number:02d}_frames')
        
        print("📹 Step 1/5: Detecting scene changes...")
        scenes = self.video_processor.detect_scene_changes(video_path, threshold=30.0)
        
        if len(scenes) == 0:
            print("   ⚠️  No scenes detected, falling back to frame extraction")
            frames = self.video_processor.extract_frames(video_path, output_dir=frames_dir)
            scene_timestamps = [f[1] for f in frames]
        else:
            print(f"\n📹 Step 2/5: Extracting representative frames from {len(scenes)} scenes...")
            cap = cv2.VideoCapture(video_path)
            scene_timestamps = []
            
            for scene in scenes:
                cap.set(cv2.CAP_PROP_POS_FRAMES, scene['mid_frame_idx'])
                ret, frame = cap.read()
                if ret:
                    scene_timestamps.append((frame, scene['mid_timestamp']))
            
            cap.release()
            frames = scene_timestamps
        
        print(f"\n🔍 Step 3/5: Running OCR on {len(frames)} scene frames...")
        ocr_titles = self.ocr_extractor.extract_movie_titles(frames, language=self.language)
        print(f"   Found {len(ocr_titles)} potential titles via OCR")
        
        print("\n🎤 Step 4/5: Transcribing audio for each scene...")
        if scenes and len(scenes) > 0:
            print(f"   Transcribing {len(scenes)} scene segments")
            audio_titles = []
            
            for idx, scene in enumerate(scenes):
                segment_audio = self.audio_transcriber.extract_movie_titles_by_timestamps(
                    video_path,
                    [scene['mid_timestamp']],
                    language=self.language,
                    window_seconds=scene['duration'] / 2
                )
                audio_titles.extend(segment_audio)
        else:
            print("   No scenes detected, using OCR timestamps")
            if ocr_titles:
                ocr_timestamps = [title['timestamp'] for title in ocr_titles]
                audio_titles = self.audio_transcriber.extract_movie_titles_by_timestamps(
                    video_path, 
                    ocr_timestamps, 
                    language=self.language,
                    window_seconds=3.0
                )
            else:
                audio_titles = []
        
        print(f"\n✅ Step 5/5: Matching and validating titles...")
        matched_titles = self.validator.match_titles(ocr_titles, audio_titles)
        validated_titles = self.validator.validate_and_resolve(
            matched_titles,
            interactive=interactive
        )
        
        print(f"\n📝 Step 6/6: Generating markdown output...")
        markdown_content = self.markdown_generator.generate_movie_list(
            validated_titles,
            oleada_number
        )
        
        markdown_path = self.markdown_generator.save_markdown(
            markdown_content,
            f'oleada-{oleada_number:02d}'
        )
        
        print("\n" + "="*70)
        print(f"✨ Processing complete! Found {len(validated_titles)} movies")
        print("="*70 + "\n")
        
        return {
            'oleada_number': oleada_number,
            'video_path': video_path,
            'total_movies': len(validated_titles),
            'validated_titles': validated_titles,
            'markdown_path': markdown_path
        }
    
    def process_multiple_videos(
        self,
        video_paths: List[str],
        starting_oleada: int = 1,
        interactive: bool = True
    ) -> List[Dict]:
        """
        Process multiple videos sequentially.
        
        Args:
            video_paths: List of video file paths
            starting_oleada: Starting oleada number
            interactive: Whether to prompt user for low-confidence matches
            
        Returns:
            List of processing results
        """
        results = []
        
        for idx, video_path in enumerate(video_paths):
            oleada_num = starting_oleada + idx
            result = self.process_video(
                video_path,
                oleada_num,
                interactive=interactive
            )
            results.append(result)
        
        return results
    
    def generate_quarto_website(self, results: List[Dict]) -> str:
        """
        Generate complete Quarto website from processing results.
        
        Args:
            results: List of processing result dictionaries
            
        Returns:
            Path to Quarto project directory
        """
        print("\n" + "="*70)
        print("🌐 Generating Quarto Website")
        print("="*70 + "\n")
        
        oleada_numbers = [r['oleada_number'] for r in results]
        
        for result in results:
            markdown_filename = f"oleada-{result['oleada_number']:02d}.qmd"
            src_path = result['markdown_path']
            dst_path = os.path.join(self.quarto_dir, markdown_filename)
            
            with open(src_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   Copied {markdown_filename} to Quarto project")
        
        index_content = self.markdown_generator.generate_index_page(oleada_numbers)
        index_path = os.path.join(self.quarto_dir, 'index.qmd')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"   Created index.qmd")
        
        self.quarto_generator.generate_quarto_config(oleada_numbers)
        self.quarto_generator.create_styles_css()
        self.quarto_generator.create_gitignore()
        self.quarto_generator.setup_github_pages()
        self.quarto_generator.generate_readme()
        
        print("\n" + "="*70)
        print(f"✨ Quarto website generated at: {self.quarto_dir}")
        print("="*70)
        print("\nTo build the website, run:")
        print(f"  cd {self.quarto_dir}")
        print("  quarto render")
        print("\nThe site will be generated in the 'docs/' directory.")
        print("="*70 + "\n")
        
        return self.quarto_dir
