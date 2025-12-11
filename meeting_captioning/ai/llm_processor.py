"""
LLM Processor - Local AI for Video Analysis

Uses Phi-2 model (1.6 GB) for:
- Generating video summaries
- Answering questions about video content
- Timeline-aware responses based on transcript
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING

# Import llama-cpp-python
if TYPE_CHECKING:
    from llama_cpp import Llama

try:
    from llama_cpp import Llama as LlamaImpl
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LlamaImpl = None  # type: ignore
    LLAMA_CPP_AVAILABLE = False


class LLMProcessor:
    """
    Processes video reports using local Phi-2 model for AI features.
    
    Features:
    - Automatic summary generation
    - Interactive Q&A with context awareness
    - Timeline-based queries (e.g., "what was said at 2:30?")
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize LLM processor with Llama 3.2 3B model.
        
        Args:
            model_path: Path to GGUF model file (default: models/llama-3.2-3b-instruct.Q4_K_M.gguf)
        """
        self.logger = logging.getLogger(__name__)
        self.llm: Optional['Llama'] = None
        self.report_data: Optional[Dict[str, Any]] = None
        self.model_loaded = False
        
        # Determine model path
        if model_path is None:
            project_root = Path(__file__).parent.parent.parent
            model_path_obj = project_root / "models" / "llama-3.2-3b-instruct.Q4_K_M.gguf"
        else:
            model_path_obj = Path(model_path)
        
        self.model_path: Path = model_path_obj
        
        # Load model if available
        if not LLAMA_CPP_AVAILABLE:
            self.logger.warning("llama-cpp-python not installed. AI features disabled.")
            self.logger.warning("Install with: pip install llama-cpp-python")
            return
        
        if not self.model_path.exists():
            self.logger.warning(f"Model file not found: {self.model_path}")
            self.logger.warning("Download from: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF")
            self.logger.warning("Or run: python download_model.py")
            return
        
        try:
            self.logger.info(f"Loading Llama 3.2 3B model from: {self.model_path}")
            if LlamaImpl is not None:
                self.llm = LlamaImpl(
                    model_path=str(self.model_path),
                    n_ctx=8192,  # Context window (8K tokens for better accuracy)
                    n_threads=6,  # More CPU threads for faster processing
                    n_gpu_layers=0,  # Pure CPU (set >0 for GPU if available)
                    verbose=False
                )
                self.model_loaded = True
                self.logger.info("Llama 3.2 3B model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.model_loaded = False
    
    def is_available(self) -> bool:
        """Check if LLM is available for use."""
        return self.model_loaded and self.llm is not None
    
    def load_report(self, report_path: Path) -> bool:
        """
        Load video report JSON for processing.
        
        Args:
            report_path: Path to report.json file
            
        Returns:
            True if loaded successfully
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            self.logger.info(f"Loaded report: {report_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load report: {e}")
            return False
    
    def generate_summary(self, max_tokens: int = 500) -> str:
        """
        Generate executive summary of the video.
        
        Args:
            max_tokens: Maximum length of summary
            
        Returns:
            Generated summary text
        """
        if not self.is_available():
            return "AI features not available. Model not loaded."
        
        if not self.report_data:
            return "No report data loaded."
        
        try:
            # Extract key information from report
            metadata = self.report_data.get('metadata', {})
            sections = self.report_data.get('sections', [])
            transcript = self.report_data.get('transcript', [])
            
            # Build context for summary
            duration = metadata.get('duration', 0)
            duration_mins = int(duration // 60)
            
            # Get full transcript text - try sections first, then transcript
            if sections:
                transcript_text = " ".join([sec.get('text', '') for sec in sections[:20]])  # First 20 sections
            else:
                transcript_text = " ".join([seg.get('text', '') for seg in transcript[:100]])  # First 100 segments
            
            if not transcript_text or len(transcript_text.strip()) < 50:
                self.logger.error(f"Insufficient data: sections={len(sections)}, transcript={len(transcript)}, text_len={len(transcript_text)}")
                return "Insufficient transcript data for summary generation."
            
            # Build enhanced prompt with clear instructions for Llama 3.2
            prompt = f"""<|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant. Summarize video transcripts concisely.<|eot_id|><|start_header_id|>user<|end_header_id|>

Duration: {duration_mins} minutes

Transcript:
{transcript_text[:3500]}

Write a 3-4 sentence summary covering the main topic, key points, and conclusions. Be direct and specific.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            
            self.logger.info(f"Generating summary with Llama 3.2 3B from {len(sections)} sections...")
            if self.llm is None:
                return "Model not loaded"
                
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.5,  # Lower temperature for more focused output
                top_p=0.85,
                top_k=40,
                repeat_penalty=1.1,
                stop=["<|eot_id|>", "<|end_of_text|>", "<|start_header_id|>"],
                stream=False
            )
            
            if isinstance(response, dict):
                summary = response['choices'][0]['text'].strip()
                self.logger.info(f"Summary generated successfully: {len(summary)} chars")
            else:
                summary = "Error: Invalid response format"
                self.logger.error("Invalid response format from LLM")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def generate_key_points(self, max_points: int = 5) -> List[str]:
        """
        Extract key points from the video with timestamps.
        
        Args:
            max_points: Maximum number of key points
            
        Returns:
            List of key points with timestamps
        """
        if not self.is_available() or not self.report_data:
            return ["AI features not available"]
        
        try:
            sections = self.report_data.get('sections', [])
            
            # Build prompt with sections
            sections_text = ""
            for i, section in enumerate(sections[:10]):  # First 10 sections
                start_time = section.get('start_time', 0)
                mins = int(start_time // 60)
                secs = int(start_time % 60)
                text = section.get('text', '')[:200]
                sections_text += f"[{mins}:{secs:02d}] {text}\n\n"
            
            prompt = f"""<|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant. Extract key insights from transcripts concisely.<|eot_id|><|start_header_id|>user<|end_header_id|>

Extract {max_points} key points from this transcript. Each point must:
- Start with timestamp [MM:SS]
- Be one clear fact or insight
- No explanations or meta-commentary

Transcript:
{sections_text}

Key points:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            
            if self.llm is None:
                return ["Model not loaded"]
                
            self.logger.info(f"Generating {max_points} key points from {len(sections)} sections...")
                
            response = self.llm(
                prompt,
                max_tokens=600,
                temperature=0.5,  # Lower temperature for precision
                top_p=0.85,
                repeat_penalty=1.1,
                stop=["<|eot_id|>", "<|end_of_text|>", "<|start_header_id|>"],
                stream=False
            )
            
            if not isinstance(response, dict):
                self.logger.error("Invalid response format from LLM")
                return ["Error: Invalid response format"]
                
            points_text = response['choices'][0]['text'].strip()
            self.logger.info(f"LLM key points response: {points_text[:200]}...")
            
            # Parse key points - accept multiple formats
            lines = [line.strip() for line in points_text.split('\n') if line.strip()]
            points = []
            
            for line in lines:
                # Remove leading numbers, bullets, or dashes
                line = line.lstrip('0123456789.)-• ')
                if line and ('[' in line or len(line) > 10):  # Has timestamp or is substantial
                    if not line.startswith('-'):
                        line = '- ' + line
                    points.append(line)
            
            if not points:
                self.logger.warning(f"No key points parsed from response: {points_text}")
                return ["No key points extracted"]
            
            self.logger.info(f"Extracted {len(points)} key points")
            return points[:max_points]
            
        except Exception as e:
            self.logger.error(f"Error generating key points: {e}")
            return [f"Error: {str(e)}"]
    
    def answer_question(self, question: str, max_tokens: int = 300) -> str:
        """
        Answer question about the video using report context.
        
        Args:
            question: User's question
            max_tokens: Maximum length of answer
            
        Returns:
            AI-generated answer
        """
        if not self.is_available():
            return "AI features not available. Please ensure the Phi-2 model is downloaded."
        
        if not self.report_data:
            return "No video report loaded. Please process a video first."
        
        try:
            # Check for simple greetings/conversational messages
            question_lower = question.lower().strip()
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'thanks', 'thank you']
            if question_lower in greetings or len(question_lower.split()) <= 2:
                greeting_responses = {
                    'hi': "Hi! I'm here to answer questions about the video. What would you like to know?",
                    'hello': "Hello! I can help you understand the video content. What would you like to ask?",
                    'hey': "Hey there! Ask me anything about the video!",
                    'thanks': "You're welcome! Feel free to ask more questions about the video.",
                    'thank you': "You're welcome! Let me know if you have other questions!"
                }
                for greeting, response in greeting_responses.items():
                    if greeting in question_lower:
                        return response
            
            # Get relevant context from report
            metadata = self.report_data.get('metadata', {})
            transcript = self.report_data.get('transcript', [])
            sections = self.report_data.get('sections', [])
            scenes = self.report_data.get('scenes', [])
            
            duration = metadata.get('duration', 0)
            duration_mins = int(duration // 60)
            
            # Check if question asks about specific time range
            import re
            time_pattern = r'(\d+)\s*(?:min|minute|second|sec|:)?\s*(?:to|-)?\s*(\d+)?\s*(?:min|minute|second|sec)?'
            time_match = re.search(time_pattern, question.lower())
            
            transcript_text = ""
            scene_info = ""
            context_note = ""
            
            if time_match:
                # Extract time range from question
                start_time = int(time_match.group(1))
                end_time = int(time_match.group(2)) if time_match.group(2) else start_time + 1
                
                # Convert to seconds if they seem to be minutes
                if 'min' in question.lower() or start_time < 100:
                    start_time *= 60
                    end_time *= 60
                
                self.logger.info(f"Time-specific question: {start_time}s to {end_time}s")
                
                # Filter sections/transcript for time range
                relevant_sections = []
                if sections:
                    for sec in sections:
                        sec_start = sec.get('start_time', 0)
                        sec_end = sec.get('end_time', 0)
                        if (sec_start <= end_time and sec_end >= start_time):
                            relevant_sections.append(sec)
                    transcript_text = " ".join([sec.get('text', '') for sec in relevant_sections])
                else:
                    for seg in transcript:
                        seg_start = seg.get('start', 0)
                        seg_end = seg.get('end', 0)
                        if (seg_start <= end_time and seg_end >= start_time):
                            transcript_text += seg.get('text', '') + " "
                
                # Add scene information for time range
                relevant_scenes = []
                for scene in scenes:
                    scene_time = scene.get('start_time', 0)
                    if start_time <= scene_time <= end_time:
                        scene_num = scene.get('scene_number', 0)
                        scene_timestamp = f"{int(scene_time//60)}:{int(scene_time%60):02d}"
                        relevant_scenes.append(f"Scene {scene_num} at {scene_timestamp}")
                
                if relevant_scenes:
                    scene_info = f"\n\nScenes in this time range: {', '.join(relevant_scenes)}"
                
                if not transcript_text:
                    return f"No transcript data available for the time range {start_time//60}:{start_time%60:02d} to {end_time//60}:{end_time%60:02d}."
                
                context_note = f" Focus specifically on the time range {start_time//60}:{start_time%60:02d} to {end_time//60}:{end_time%60:02d}."
                
            else:
                # General question - use broader context
                if sections:
                    transcript_text = " ".join([sec.get('text', '') for sec in sections[:30]])  # First 30 sections
                else:
                    transcript_text = " ".join([seg.get('text', '') for seg in transcript[:80]])  # More context
                
                # Add scene timeline overview (first 10 scenes)
                if scenes and len(scenes) > 0:
                    scene_list = []
                    for scene in scenes[:10]:
                        scene_num = scene.get('scene_number', 0)
                        scene_time = scene.get('start_time', 0)
                        scene_timestamp = f"{int(scene_time//60)}:{int(scene_time%60):02d}"
                        scene_list.append(f"Scene {scene_num} at {scene_timestamp}")
                    scene_info = f"\n\nVideo scenes timeline: {', '.join(scene_list)}"
                    if len(scenes) > 10:
                        scene_info += f" (and {len(scenes) - 10} more)"
                
                # Check if question asks about timing in general
                if any(word in question.lower() for word in ['when', 'time', 'timestamp']):
                    context_note = " Include specific timestamps in your answer."
            
            # Build enhanced prompt for Llama 3.2
            prompt = f"""<|start_header_id|>system<|end_header_id|>

You are a friendly, helpful AI assistant that answers questions about video content. Be natural and conversational while staying accurate.<|eot_id|><|start_header_id|>user<|end_header_id|>

Video Duration: {duration_mins} minutes{scene_info}

Transcript:
{transcript_text[:4000]}

Question: {question}{context_note}

Provide a clear, natural answer based on the transcript above.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            
            self.logger.info(f"Answering question: {question}")
            if self.llm is None:
                return "Model not loaded"
                
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.4,  # Even lower temperature for factual accuracy
                top_p=0.85,
                top_k=40,
                repeat_penalty=1.15,
                stop=["<|eot_id|>", "<|end_of_text|>", "<|start_header_id|>"],
                stream=False
            )
            
            if isinstance(response, dict):
                answer = response['choices'][0]['text'].strip()
            else:
                answer = "Error: Invalid response format"
            self.logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            self.logger.error(f"Error answering question: {e}")
            return f"Error generating answer: {str(e)}"
    
    def get_timeline_info(self, timestamp: str) -> str:
        """
        Get information about what happened at a specific timestamp.
        
        Args:
            timestamp: Time in format "MM:SS" or seconds
            
        Returns:
            Information about that timestamp
        """
        if not self.report_data:
            return "No report data available"
        
        try:
            # Parse timestamp
            if ':' in timestamp:
                parts = timestamp.split(':')
                time_seconds = int(parts[0]) * 60 + int(parts[1])
            else:
                time_seconds = float(timestamp)
            
            # Find closest transcript segment
            transcript = self.report_data.get('transcript', [])
            closest_seg = None
            min_diff = float('inf')
            
            for seg in transcript:
                seg_time = seg.get('start', 0)
                diff = abs(seg_time - time_seconds)
                if diff < min_diff:
                    min_diff = diff
                    closest_seg = seg
            
            if closest_seg:
                text = closest_seg.get('text', 'No text available')
                start = closest_seg.get('start', 0)
                mins = int(start // 60)
                secs = int(start % 60)
                return f"At {mins}:{secs:02d}: {text}"
            else:
                return "No information found for that timestamp"
                
        except Exception as e:
            return f"Error: {str(e)}"
