"""
Main application orchestrator for the meeting video captioning pipeline.

This module coordinates all processing steps from input to final outputs.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from meeting_captioning.config import Config
from meeting_captioning.io.video_loader import VideoLoader
from meeting_captioning.io.file_manager import FileManager
from meeting_captioning.processing.video_processor import VideoProcessor
from meeting_captioning.processing.caption_generator import CaptionGenerator, Caption
from meeting_captioning.transcription.transcriber import Transcriber
from meeting_captioning.transcription.segmenter import TranscriptionSegmenter
from meeting_captioning.reporting.report_builder import ReportBuilder
from meeting_captioning.reporting.json_exporter import JSONExporter
from meeting_captioning.utils.logging_config import setup_logging, LoggerMixin
from meeting_captioning.utils.error_handling import MeetingCaptioningError, ProcessingError


@dataclass
class PipelineResult:
    """Results from the complete processing pipeline."""
    success: bool
    session_dir: Path
    captioned_video_path: Optional[Path] = None
    report_paths: Dict[str, Path] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.report_paths is None:
            self.report_paths = {}


class MeetingCaptioningApp(LoggerMixin):
    """
    Main application class orchestrating the entire pipeline.
    
    Single-click workflow:
    1. Load video (local/URL/YouTube)
    2. Extract audio
    3. Detect scenes
    4. Transcribe audio
    5. Generate captions
    6. Burn captions into video
    7. Generate JSON master report (convert to PDF/DOCX/TXT on-demand)
    """
    
    def __init__(
        self,
        session_name: Optional[str] = None
    ):
        """
        Initialize the application.
        
        Args:
            session_name: Name for this processing session
        """
        # Setup logging (LoggerMixin provides self.logger via property)
        setup_logging("meeting_captioning_app")
        
        # Initialize components
        self.video_loader = VideoLoader()
        self.file_manager = FileManager(session_name)
        self.video_processor = VideoProcessor()
        self.transcriber = Transcriber()
        self.segmenter = TranscriptionSegmenter()
        self.caption_generator = CaptionGenerator()
        self.report_builder = ReportBuilder()
        
        # Exporter (JSON only - other formats via /api/convert-report)
        self.json_exporter = JSONExporter()
        
        # Progress tracking
        self.progress_callback = None
        
        self.logger.info("Meeting Captioning App initialized")
        self.logger.info(f"Output directory: {self.file_manager.session_dir}")
    
    def _update_progress(self, percent: int, message: str) -> None:
        """Update progress via callback and logging."""
        self.logger.info(f"Progress {percent}%: {message}")
        if self.progress_callback:
            try:
                self.progress_callback(percent, message)
            except Exception as e:
                self.logger.warning(f"Progress callback error: {e}")
    
    def process_video(
        self,
        video_source: str,
        model_size: str = "base",
        language: Optional[str] = None,
        output_dir: Optional[Path] = None,
        burn_captions: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        threshold: Optional[float] = None,
        min_scene_duration: Optional[float] = None
    ) -> PipelineResult:
        """
        Run the complete processing pipeline.
        
        Args:
            video_source: Video file path or URL
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Target language (None for auto-detect)
            output_dir: Custom output directory (None for default)
            burn_captions: Whether to burn captions into video
            progress_callback: Callback function(progress_percent, message)
            threshold: Scene detection threshold (None for default)
            min_scene_duration: Minimum scene duration (None for default)
            
        Returns:
            PipelineResult with all outputs
        """
        # Set progress callback
        self.progress_callback = progress_callback
        
        # Update file manager if custom output directory specified
        if output_dir:
            self.file_manager = FileManager(session_name=output_dir.name)
            self.file_manager.session_dir = output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Starting pipeline for: {video_source}")
        self._update_progress(0, "Starting processing...")
        
        try:
            # Step 1: Load video (10%)
            # Determine if downloading is needed and show appropriate message
            if isinstance(video_source, str) and video_source.startswith(('http://', 'https://')):
                if 'youtube.com' in video_source or 'youtu.be' in video_source:
                    self._update_progress(5, "Downloading from YouTube...")
                elif 'drive.google.com' in video_source:
                    self._update_progress(5, "Downloading from Google Drive...")
                elif 'dropbox.com' in video_source:
                    self._update_progress(5, "Downloading from Dropbox...")
                else:
                    self._update_progress(5, "Downloading from cloud storage...")
            else:
                self._update_progress(5, "Loading video...")
            
            video_path = self.video_loader.load_video(video_source)
            metadata = self.video_loader.validate_video(video_path)
            self._update_progress(10, f"Video loaded: {video_path.name}")
            
            # Step 2: Process video - extract audio & detect scenes (30%)
            self._update_progress(15, "Processing video...")
            
            # Create scene detector with custom parameters if provided
            from meeting_captioning.processing.scene_detector import SceneDetector
            scene_detector = SceneDetector(
                threshold=threshold,
                min_scene_duration=min_scene_duration
            )
            self.video_processor.scene_detector = scene_detector
            
            def frame_callback(frame_data, frame_num, timestamp):
                return self.file_manager.save_frame(frame_data, frame_num, timestamp)
            
            processing_results = self.video_processor.process_video(
                video_path,
                extract_audio=True,
                detect_scenes=True,
                frame_callback=frame_callback,
                audio_output_path=self.file_manager.get_audio_output_path("audio.wav")
            )
            
            audio_path = processing_results['audio_path']
            scenes = processing_results['scenes']
            self._update_progress(30, f"Detected {len(scenes)} scenes")
            
            # Validate audio extraction
            if not audio_path:
                raise ProcessingError(
                    "Audio extraction failed. The video may not have an audio track, "
                    "or the audio extraction process failed. Please check the video file."
                )
            
            if not audio_path.exists():
                raise ProcessingError(
                    f"Audio file not found after extraction: {audio_path}. "
                    "The audio extraction may have failed."
                )
            
            self.logger.info(f"Audio file ready for transcription: {audio_path} ({audio_path.stat().st_size} bytes)")
            
            # Step 3: Transcribe audio (50%)
            self._update_progress(35, "Transcribing audio...")
            
            # Create transcriber with custom model and language
            transcriber = Transcriber(model_size=model_size, language=language)
            segments = transcriber.transcribe_to_segments(audio_path)
            
            # Save transcription
            transcript_result = transcriber.transcribe(audio_path)
            full_transcript = transcript_result['text']
            
            # Save transcript to text file
            transcript_txt_path = self.file_manager.get_transcript_output_path('transcript.txt')
            with open(transcript_txt_path, 'w', encoding='utf-8') as f:
                f.write(full_transcript)
            
            self._update_progress(50, f"Transcribed {len(segments)} segments")
            
            # Step 4: Segment transcription (60%)
            self._update_progress(55, "Segmenting transcript...")
            sections = self.segmenter.segment_by_pauses(segments)
            
            # Summarize sections
            for section in sections:
                section.summary = self.segmenter.summarize_section(section)
                section.key_points = self.segmenter.extract_key_points(section)
            
            self._update_progress(60, f"Created {len(sections)} sections")
            
            # Step 5: Generate captions (70%)
            self._update_progress(65, "Generating captions...")
            captions = [
                Caption(
                    index=i + 1,
                    start_time=seg.start,
                    end_time=seg.end,
                    text=seg.text
                )
                for i, seg in enumerate(segments)
            ]
            
            srt_path = self.file_manager.get_caption_file_path("srt")
            self.caption_generator.create_srt_file(captions, srt_path)
            self._update_progress(70, "Captions generated")
            
            # Step 6: Burn captions into video (80%) - Optional
            actual_output_path = None
            if burn_captions:
                self._update_progress(75, "Burning captions into video...")
                output_video_name = f"{video_path.stem}_captioned.mp4"
                output_video_path = self.file_manager.get_video_output_path(output_video_name)
                
                # burn_captions returns the actual sanitized path (may differ from input)
                actual_output_path = self.caption_generator.burn_captions(
                    video_path,
                    srt_path,
                    output_video_path
                )
                self._update_progress(80, "Captioned video created")
            else:
                self._update_progress(80, "Skipped caption burning (use SRT file for playback)")
            
            # Step 7: Build report (85%)
            self._update_progress(82, "Building report...")
            report = self.report_builder.build_report(
                video_path=video_path,
                duration=metadata['duration'],
                scenes=scenes,
                sections=sections,
                full_transcript=full_transcript,
                metadata=metadata
            )
            self._update_progress(85, "Report built")
            
            # Step 8: Export JSON master report (95%)
            self._update_progress(88, "Exporting report...")
            report_paths = {}
            
            # Always save JSON master report (storage efficient, single source of truth)
            json_path = self.file_manager.get_report_output_path("report", "json")
            self.json_exporter.export(report, json_path)
            report_paths['json'] = json_path
            self._update_progress(90, "Master report saved (JSON)")
            
            # Note: PDF/DOCX/TXT can be generated on-demand via /api/convert-report
            
            # Step 9: Create manifest and finalize (100%)
            self._update_progress(98, "Finalizing...")
            self.file_manager.create_manifest()
            
            self._update_progress(100, "Processing complete!")
            
            # Return results
            result = PipelineResult(
                success=True,
                session_dir=self.file_manager.session_dir,
                captioned_video_path=actual_output_path,  # Use the actual sanitized path
                report_paths=report_paths
            )
            
            self.logger.info("Pipeline completed successfully")
            self.logger.info(f"Outputs in: {self.file_manager.session_dir}")
            
            return result
            
        except MeetingCaptioningError as e:
            self.logger.error(f"Pipeline failed: {e}")
            return PipelineResult(
                success=False,
                session_dir=self.file_manager.session_dir,
                error=str(e)
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return PipelineResult(
                success=False,
                session_dir=self.file_manager.session_dir,
                error=f"Unexpected error: {str(e)}"
            )
    
    def cleanup(self) -> None:
        """Cleanup temporary files."""
        self.logger.info("Cleaning up...")
        self.video_loader.cleanup_temp_files()
        self.file_manager.cleanup_frames()
