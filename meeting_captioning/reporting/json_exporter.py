"""JSON export module for storage-efficient master reports."""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

from meeting_captioning.reporting.report_builder import Report
from meeting_captioning.utils.logging_config import LoggerMixin
from meeting_captioning.utils.error_handling import ReportGenerationError


class JSONExporter(LoggerMixin):
    """Exports reports to JSON format - the single source of truth."""
    
    def export(self, report: Report, output_path: Path) -> Path:
        """
        Export report to JSON format.
        
        This creates a compact, storage-efficient master report that
        can be converted to other formats on-demand without reprocessing.
        
        Args:
            report: Report object
            output_path: Output JSON file path
            
        Returns:
            Path to generated JSON file
        """
        self.logger.info(f"Exporting report to JSON: {output_path}")
        
        try:
            # Convert Report object to serializable dictionary
            report_data = {
                "title": report.title,
                "date": report.date.isoformat(),
                "video_path": str(report.video_path),
                "duration": report.duration,
                "summary": report.summary,
                "key_points": report.key_points,
                "full_transcript": report.full_transcript,
                "metadata": report.metadata,
                
                # Scenes
                "scenes": [
                    {
                        "scene_number": scene.scene_number,
                        "start_time": scene.start_time,
                        "end_time": scene.end_time,
                        "start_frame": scene.start_frame,
                        "end_frame": scene.end_frame,
                        "frame_path": str(scene.frame_path) if scene.frame_path else None,
                        "description": scene.description if hasattr(scene, 'description') else ""
                    }
                    for scene in report.scenes
                ],
                
                # Transcript sections
                "sections": [
                    {
                        "start_time": section.start_time,
                        "end_time": section.end_time,
                        "text": section.text,
                        "summary": section.summary if hasattr(section, 'summary') else "",
                        "key_points": section.key_points if hasattr(section, 'key_points') else []
                    }
                    for section in report.sections
                ]
            }
            
            # Write JSON with compact formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            file_size_kb = output_path.stat().st_size / 1024
            self.logger.info(f"JSON exported: {output_path} ({file_size_kb:.1f} KB)")
            return output_path
            
        except Exception as e:
            raise ReportGenerationError(f"JSON export failed", e)
    
    def load(self, json_path: Path) -> Dict[str, Any]:
        """
        Load report data from JSON file.
        
        Args:
            json_path: Path to JSON report file
            
        Returns:
            Dictionary containing report data
        """
        self.logger.info(f"Loading report from JSON: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Convert ISO date string back to datetime
            if 'date' in report_data:
                report_data['date'] = datetime.fromisoformat(report_data['date'])
            
            self.logger.info(f"JSON report loaded: {json_path}")
            return report_data
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to load JSON report", e)
