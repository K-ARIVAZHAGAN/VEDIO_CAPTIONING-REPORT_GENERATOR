"""
Report builder module for creating structured meeting reports.

This module builds comprehensive reports from video processing results.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from meeting_captioning.processing.scene_detector import Scene
from meeting_captioning.transcription.segmenter import TranscriptSection
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.time_utils import format_timestamp


@dataclass
class Report:
    """
    Comprehensive meeting report data structure.
    
    Contains all information needed for export to various formats.
    """
    title: str
    date: datetime
    video_path: Path
    duration: float
    scenes: List[Scene] = field(default_factory=list)
    sections: List[TranscriptSection] = field(default_factory=list)
    full_transcript: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    key_points: List[str] = field(default_factory=list)


class ReportBuilder(LoggerMixin):
    """
    Builds comprehensive reports from processing results.
    
    Aggregates data from video processing, scene detection,
    and transcription to create structured reports.
    """
    
    def __init__(self):
        """Initialize report builder."""
        self.logger.info("Report builder initialized")
    
    def build_report(
        self,
        video_path: Path,
        duration: float,
        scenes: List[Scene],
        sections: List[TranscriptSection],
        full_transcript: str = "",
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Report:
        """
        Build a comprehensive report.
        
        Args:
            video_path: Path to source video
            duration: Video duration in seconds
            scenes: List of detected scenes
            sections: List of transcript sections
            full_transcript: Full transcription text
            title: Report title (auto-generated if None)
            metadata: Additional metadata
            
        Returns:
            Report object
        """
        self.logger.info("Building report")
        
        if title is None:
            title = f"Meeting Report - {video_path.stem}"
        
        if metadata is None:
            metadata = {}
        
        report = Report(
            title=title,
            date=datetime.now(),
            video_path=video_path,
            duration=duration,
            scenes=scenes,
            sections=sections,
            full_transcript=full_transcript,
            metadata=metadata
        )
        
        # Generate summary
        report.summary = self._generate_summary(report)
        
        # Extract key points
        report.key_points = self._extract_key_points(sections)
        
        self.logger.info(
            f"Report built: {len(scenes)} scenes, "
            f"{len(sections)} sections, {len(full_transcript)} chars"
        )
        
        return report
    
    def _generate_summary(self, report: Report) -> str:
        """Generate report summary."""
        duration_min = report.duration / 60
        
        summary = (
            f"Meeting video analyzed: {report.video_path.name}\n"
            f"Duration: {duration_min:.1f} minutes\n"
            f"Scenes detected: {len(report.scenes)}\n"
            f"Transcript sections: {len(report.sections)}\n"
        )
        
        return summary
    
    def _extract_key_points(
        self,
        sections: List[TranscriptSection]
    ) -> List[str]:
        """Extract key points from all sections."""
        key_points = []
        
        for section in sections:
            if section.key_points:
                key_points.extend(section.key_points)
        
        # Limit to top 10 key points
        return key_points[:10]
    
    def add_scene_descriptions(
        self,
        report: Report,
        descriptions: Dict[int, str]
    ) -> None:
        """
        Add descriptions to scenes in report.
        
        Args:
            report: Report object
            descriptions: Dictionary mapping scene_number to description
        """
        for scene in report.scenes:
            if scene.scene_number in descriptions:
                scene.description = descriptions[scene.scene_number]
    
    def format_report_text(self, report: Report) -> str:
        """
        Format report as plain text.
        
        Args:
            report: Report object
            
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append(report.title.center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Date: {report.date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Video: {report.video_path.name}")
        lines.append(f"Duration: {format_timestamp(report.duration, format_type='readable')}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(report.summary)
        lines.append("")
        
        # Key Points
        if report.key_points:
            lines.append("KEY POINTS")
            lines.append("-" * 80)
            for i, point in enumerate(report.key_points, 1):
                lines.append(f"{i}. {point}")
            lines.append("")
        
        # Scenes
        lines.append("SCENE BREAKDOWN")
        lines.append("-" * 80)
        for scene in report.scenes:
            lines.append(
                f"Scene {scene.scene_number}: "
                f"{format_timestamp(scene.start_time)} - "
                f"{format_timestamp(scene.end_time or report.duration)}"
            )
            if scene.description:
                lines.append(f"  Description: {scene.description}")
            lines.append("")
        
        # Transcript Sections
        lines.append("TRANSCRIPT")
        lines.append("-" * 80)
        for section in report.sections:
            lines.append(
                f"\n[{format_timestamp(section.start_time)} - "
                f"{format_timestamp(section.end_time)}]"
            )
            lines.append(section.text)
            lines.append("")
        
        return "\n".join(lines)
