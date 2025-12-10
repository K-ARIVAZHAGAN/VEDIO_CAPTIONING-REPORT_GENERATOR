"""
Segmentation module for organizing transcription into logical sections.

This module segments transcripts based on content, pauses, and context.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os

from meeting_captioning.transcription.transcriber import TranscriptionSegment
from meeting_captioning.utils.logging_config import LoggerMixin

# Import OpenAI for intelligent summarization
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class TranscriptSection:
    """Represents a logical section of transcript."""
    section_number: int
    start_time: float
    end_time: float
    segments: List[TranscriptionSegment]
    summary: str = ""
    key_points: List[str] = None
    
    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []
    
    @property
    def text(self) -> str:
        """Get combined text of all segments."""
        return " ".join(seg.text for seg in self.segments)
    
    @property
    def duration(self) -> float:
        """Get section duration."""
        return self.end_time - self.start_time


class TranscriptionSegmenter(LoggerMixin):
    """
    Segments transcriptions into logical sections.
    
    Uses heuristics:
    - Long pauses between speech
    - Topic changes
    - Time-based chunking
    """
    
    def __init__(
        self,
        pause_threshold: float = 2.0,
        max_section_duration: float = 300.0,
        min_section_duration: float = 30.0,
        enable_llm: bool = True
    ):
        """
        Initialize segmenter.
        
        Args:
            pause_threshold: Pause duration to trigger new section (seconds)
            max_section_duration: Maximum section length (seconds)
            min_section_duration: Minimum section length (seconds)
            enable_llm: Enable LLM-based intelligent summarization
        """
        self.pause_threshold = pause_threshold
        self.max_section_duration = max_section_duration
        self.min_section_duration = min_section_duration
        self.enable_llm = enable_llm
        
        # Initialize OpenAI client if available and enabled
        self.openai_client = None
        if enable_llm and OPENAI_AVAILABLE:
            try:
                # Try to import config
                try:
                    import config
                    api_key = getattr(config, 'OPENAI_API_KEY', None)
                except ImportError:
                    api_key = None
                
                # Fall back to environment variable
                if not api_key or api_key == 'YOUR_OPENAI_API_KEY':
                    api_key = os.environ.get('OPENAI_API_KEY')
                
                if api_key and api_key != 'YOUR_OPENAI_API_KEY':
                    self.openai_client = OpenAI(api_key=api_key)
                    self.logger.info("OpenAI client initialized for intelligent summarization")
                else:
                    self.logger.warning("OpenAI API key not configured - using basic summarization")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {e}")
        elif enable_llm and not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI package not installed - using basic summarization")
        
        self.logger.info("Transcription segmenter initialized")
    
    def segment_by_pauses(
        self,
        segments: List[TranscriptionSegment]
    ) -> List[TranscriptSection]:
        """
        Segment transcription based on pauses.
        
        Args:
            segments: List of transcription segments
            
        Returns:
            List of transcript sections
        """
        self.logger.info(f"Segmenting {len(segments)} segments by pauses")
        
        if not segments:
            return []
        
        sections = []
        current_section_segments = []
        section_number = 1
        section_start_time = segments[0].start
        
        for i, segment in enumerate(segments):
            current_section_segments.append(segment)
            
            # Check if we should start a new section
            should_break = False
            
            # Check pause duration to next segment
            if i < len(segments) - 1:
                pause = segments[i + 1].start - segment.end
                if pause >= self.pause_threshold:
                    should_break = True
            
            # Check max section duration
            section_duration = segment.end - section_start_time
            if section_duration >= self.max_section_duration:
                should_break = True
            
            # Create section if breaking or at end
            if should_break or i == len(segments) - 1:
                if current_section_segments:
                    section = TranscriptSection(
                        section_number=section_number,
                        start_time=section_start_time,
                        end_time=current_section_segments[-1].end,
                        segments=current_section_segments.copy()
                    )
                    sections.append(section)
                    
                    section_number += 1
                    current_section_segments = []
                    if i < len(segments) - 1:
                        section_start_time = segments[i + 1].start
        
        self.logger.info(f"Created {len(sections)} sections")
        return sections
    
    def segment_by_time(
        self,
        segments: List[TranscriptionSegment],
        interval: float = 60.0
    ) -> List[TranscriptSection]:
        """
        Segment transcription by fixed time intervals.
        
        Args:
            segments: List of transcription segments
            interval: Time interval in seconds
            
        Returns:
            List of transcript sections
        """
        self.logger.info(f"Segmenting by {interval}s intervals")
        
        if not segments:
            return []
        
        sections = []
        section_number = 1
        current_time = 0.0
        current_section_segments = []
        
        for segment in segments:
            # Check if segment crosses interval boundary
            if segment.start >= current_time + interval:
                # Save current section
                if current_section_segments:
                    section = TranscriptSection(
                        section_number=section_number,
                        start_time=current_section_segments[0].start,
                        end_time=current_section_segments[-1].end,
                        segments=current_section_segments.copy()
                    )
                    sections.append(section)
                    section_number += 1
                
                # Start new section
                current_section_segments = []
                current_time = segment.start
            
            current_section_segments.append(segment)
        
        # Add final section
        if current_section_segments:
            section = TranscriptSection(
                section_number=section_number,
                start_time=current_section_segments[0].start,
                end_time=current_section_segments[-1].end,
                segments=current_section_segments
            )
            sections.append(section)
        
        self.logger.info(f"Created {len(sections)} time-based sections")
        return sections
    
    def summarize_section(self, section: TranscriptSection) -> str:
        """
        Generate intelligent summary for a section using LLM.
        
        Falls back to basic summarization if LLM is unavailable.
        
        Args:
            section: Transcript section
            
        Returns:
            Summary text
        """
        text = section.text
        word_count = len(text.split())
        duration_min = section.duration / 60
        
        # Use LLM if available
        if self.openai_client:
            try:
                self.logger.info(f"Generating LLM summary for section {section.section_number}")
                
                prompt = f"""Summarize the following video transcript segment in 2-3 concise sentences. 
Focus on the main topics, key information, and important points discussed.

Transcript ({word_count} words, {duration_min:.1f} minutes):
{text}

Summary:"""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Using cost-effective model
                    messages=[
                        {"role": "system", "content": "You are an expert at summarizing video transcripts. Provide clear, concise summaries that capture the main points."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                summary = response.choices[0].message.content.strip()
                self.logger.info("LLM summary generated successfully")
                return f"{summary} ({word_count} words, {duration_min:.1f} min)"
                
            except Exception as e:
                self.logger.warning(f"LLM summarization failed: {e}, falling back to basic summary")
        
        # Fallback: Basic summary
        if len(text) <= 100:
            summary = text
        else:
            summary = text[:100] + "..."
        
        return f"{summary} ({word_count} words, {duration_min:.1f} min)"
    
    def extract_key_points(
        self,
        section: TranscriptSection,
        max_points: int = 5
    ) -> List[str]:
        """
        Extract key points from section using intelligent LLM analysis.
        
        Falls back to keyword-based extraction if LLM is unavailable.
        
        Args:
            section: Transcript section
            max_points: Maximum number of key points
            
        Returns:
            List of key point strings
        """
        text = section.text
        
        # Use LLM if available
        if self.openai_client:
            try:
                self.logger.info(f"Extracting LLM key points for section {section.section_number}")
                
                prompt = f"""Extract the {max_points} most important key points from this video transcript segment.
Focus on:
- Main topics discussed
- Important facts or information
- Action items or decisions
- Critical insights or conclusions

Format as a bulleted list.

Transcript:
{text}

Key Points:"""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing video transcripts and extracting key information. Provide clear, actionable key points."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.3
                )
                
                # Parse the response into list items
                content = response.choices[0].message.content.strip()
                key_points = []
                for line in content.split('\n'):
                    line = line.strip()
                    # Remove bullet points and numbering
                    if line.startswith(('-', '•', '*')):
                        line = line[1:].strip()
                    elif line and line[0].isdigit() and '.' in line[:3]:
                        line = line.split('.', 1)[1].strip()
                    
                    if line:
                        key_points.append(line)
                
                if key_points:
                    self.logger.info(f"Extracted {len(key_points)} LLM key points")
                    return key_points[:max_points]
                
            except Exception as e:
                self.logger.warning(f"LLM key point extraction failed: {e}, falling back to keyword-based")
        
        # Fallback: Simple keyword-based extraction
        sentences = text.split('. ')
        
        key_indicators = [
            'important', 'key', 'critical', 'note that',
            'remember', 'focus on', 'main', 'primary'
        ]
        
        key_points = []
        for sentence in sentences[:max_points]:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in key_indicators):
                key_points.append(sentence)
        
        # If no key indicators found, just take first few sentences
        if not key_points:
            key_points = [s.strip() for s in sentences[:max_points] if s.strip()]
        
        return key_points[:max_points]
