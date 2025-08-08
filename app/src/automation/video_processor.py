# app/src/automation/video_processor.py
# Updated to use the new transitions module with proper class structure

import os
import shutil
from typing import Optional, List, Tuple

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CONNECTORS_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "connectors")
QUIZ_OUTRO_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "quiz_outro")

# Default settings
DEFAULT_TRANSITION_TYPE = "fade"
DEFAULT_TRANSITION_DURATION = 0.25
DEFAULT_FFMPEG_PRESET = "faster"

class VideoProcessor:
    """
    Video processor class for handling video concatenation with transitions
    """
    
    def __init__(self, use_transitions: bool = True, 
                 transition_type: str = DEFAULT_TRANSITION_TYPE,
                 transition_duration: float = DEFAULT_TRANSITION_DURATION):
        """
        Initialize VideoProcessor with configuration
        
        Args:
            use_transitions: Whether to use transitions between videos
            transition_type: Type of transition (fade, slide, wipe, dissolve, etc.)
            transition_duration: Duration of transitions in seconds
        """
        self.use_transitions = use_transitions
        self.transition_type = transition_type
        self.transition_duration = transition_duration
        self.ffmpeg_preset = DEFAULT_FFMPEG_PRESET
        
        # Paths configuration
        self.connectors_path = CONNECTORS_PATH
        self.quiz_outro_path = QUIZ_OUTRO_PATH
        
        print(f"🎬 VideoProcessor initialized")
        if self.use_transitions:
            print(f"   ✨ Transitions: {self.transition_type} ({self.transition_duration}s)")
    
    def process_video_sequence(self, client_video: str, output_path: str, 
                              target_width: int, target_height: int,
                              processing_mode: str = "connector_quiz") -> Optional[str]:
        """
        Process video sequence with optional transitions
        
        Args:
            client_video: Path to client video
            output_path: Output file path
            target_width: Target width
            target_height: Target height
            processing_mode: One of "connector_quiz", "quiz_only", or "save_only"
        
        Returns:
            None on success, error message on failure
        """
        print(f"🎬 Starting video processing in {processing_mode} mode...")
        if self.use_transitions:
            print(f"   ✨ Transitions: {self.transition_type} ({self.transition_duration}s)")
        
        # Handle save_only mode (just copy)
        if processing_mode == "save_only":
            try:
                shutil.copy2(client_video, output_path)
                print(f"✅ Video copied successfully")
                return None
            except Exception as e:
                return f"Copy failed: {e}"
        
        # Build video list based on processing mode
        video_list = [client_video]
        
        if processing_mode == "connector_quiz":
            # Add connector
            connector = self._get_connector_video()
            if connector:
                video_list.append(connector)
                print(f"✅ Added connector: {os.path.basename(connector)}")
            
            # Add quiz outro
            quiz = self._get_quiz_video()
            if quiz:
                video_list.append(quiz)
                print(f"✅ Added quiz outro: {os.path.basename(quiz)}")
        
        elif processing_mode == "quiz_only":
            # Add only quiz outro
            quiz = self._get_quiz_video()
            if quiz:
                video_list.append(quiz)
                print(f"✅ Added quiz outro: {os.path.basename(quiz)}")
        
        # Process with or without transitions
        if self.use_transitions and len(video_list) > 1:
            print(f"🎞️ Applying {self.transition_type} transitions...")
            try:
                from .transitions import apply_transitions_to_video
                return apply_transitions_to_video(
                    video_list, 
                    output_path, 
                    target_width, 
                    target_height,
                    self.transition_type,
                    self.transition_duration
                )
            except ImportError as e:
                print(f"⚠️ Transitions module not available: {e}")
                return self._fallback_concat(video_list, output_path, target_width, target_height)
        else:
            # Use simple concatenation
            return self._fallback_concat(video_list, output_path, target_width, target_height)
    
    def _get_connector_video(self) -> Optional[str]:
        """Get the first available connector video"""
        if not os.path.exists(self.connectors_path):
            print(f"⚠️ Connector directory not found: {self.connectors_path}")
            return None
        
        files = [f for f in os.listdir(self.connectors_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(self.connectors_path, files[0])
        
        print(f"⚠️ No connector videos found")
        return None
    
    def _get_quiz_video(self) -> Optional[str]:
        """Get the first available quiz outro video"""
        if not os.path.exists(self.quiz_outro_path):
            print(f"⚠️ Quiz outro directory not found: {self.quiz_outro_path}")
            return None
        
        files = [f for f in os.listdir(self.quiz_outro_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(self.quiz_outro_path, files[0])
        
        print(f"⚠️ No quiz outro videos found")
        return None
    
    def _fallback_concat(self, video_list: List[str], output_path: str, 
                        target_width: int, target_height: int) -> Optional[str]:
        """Fallback concatenation without transitions"""
        try:
            from .transitions.processor import TransitionProcessor
            processor = TransitionProcessor()
            return processor._fallback_concat(video_list, output_path, target_width, target_height)
        except ImportError:
            # Ultimate fallback - basic ffmpeg concat
            return self._basic_concat(video_list, output_path, target_width, target_height)
    
    def _basic_concat(self, video_list: List[str], output_path: str,
                     target_width: int, target_height: int) -> Optional[str]:
        """Basic concatenation using ffmpeg directly"""
        import subprocess
        import tempfile
        
        try:
            # Create a temporary file list for ffmpeg
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for video in video_list:
                    f.write(f"file '{video}'\n")
                list_file = f.name
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', list_file,
                '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2',
                '-c:v', 'libx264', '-preset', self.ffmpeg_preset,
                '-c:a', 'aac', '-b:a', '128k',
                output_path
            ]
            
            # Execute ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.unlink(list_file)
            
            if result.returncode == 0:
                print(f"✅ Videos concatenated successfully")
                return None
            else:
                return f"FFmpeg error: {result.stderr}"
                
        except Exception as e:
            return f"Concatenation failed: {e}"
    
    def configure_transitions(self, enabled: bool = True, 
                            transition_type: str = None, 
                            duration: float = None):
        """
        Configure transition settings
        
        Args:
            enabled: Whether to use transitions
            transition_type: Type of transition to use
            duration: Transition duration in seconds
        """
        self.use_transitions = enabled
        
        if transition_type is not None:
            self.transition_type = transition_type
        
        if duration is not None:
            self.transition_duration = max(0.1, min(2.0, duration))
        
        print(f"✅ Transitions configured:")
        print(f"   Enabled: {self.use_transitions}")
        if self.use_transitions:
            print(f"   Type: {self.transition_type}")
            print(f"   Duration: {self.transition_duration}s")
    
    def get_video_dimensions(self, video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Get video dimensions (for backward compatibility)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (width, height, error_message)
        """
        try:
            from .transitions.video_info import VideoInfo
            width, height = VideoInfo.get_dimensions(video_path)
            if width and height:
                return width, height, None
            return None, None, "Could not get video dimensions"
        except ImportError:
            # Fallback to ffprobe
            return self._get_dimensions_ffprobe(video_path)
    
    def _get_dimensions_ffprobe(self, video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """Get video dimensions using ffprobe"""
        import subprocess
        import json
        
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'json',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('streams'):
                    stream = data['streams'][0]
                    width = stream.get('width')
                    height = stream.get('height')
                    if width and height:
                        return width, height, None
            
            return None, None, "Could not get video dimensions"
            
        except Exception as e:
            return None, None, f"Error getting dimensions: {e}"
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    
    def validate_video_file(self, file_path: str) -> bool:
        """
        Validate if a file is a supported video format
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if valid video file, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_supported_formats()


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# These maintain compatibility with existing code that uses the old functions
# ============================================================================

# Global instance for backward compatibility
_default_processor = None

def _get_default_processor() -> VideoProcessor:
    """Get or create default processor instance"""
    global _default_processor
    if _default_processor is None:
        _default_processor = VideoProcessor()
    return _default_processor

def process_video_sequence(client_video: str, output_path: str, 
                          target_width: int, target_height: int,
                          processing_mode: str = "connector_quiz") -> Optional[str]:
    """
    Backward compatibility wrapper for process_video_sequence
    
    Args:
        client_video: Path to client video
        output_path: Output file path
        target_width: Target width
        target_height: Target height
        processing_mode: One of "connector_quiz", "quiz_only", or "save_only"
    
    Returns:
        None on success, error message on failure
    """
    processor = _get_default_processor()
    return processor.process_video_sequence(
        client_video, output_path, target_width, target_height, processing_mode
    )

def configure_transitions(enabled: bool = True, 
                        transition_type: str = "fade", 
                        duration: float = 0.25):
    """
    Backward compatibility wrapper for configure_transitions
    
    Args:
        enabled: Whether to use transitions
        transition_type: Type of transition to use
        duration: Transition duration in seconds
    """
    processor = _get_default_processor()
    processor.configure_transitions(enabled, transition_type, duration)

def get_video_dimensions(video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """
    Backward compatibility wrapper for get_video_dimensions
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple of (width, height, error_message)
    """
    processor = _get_default_processor()
    return processor.get_video_dimensions(video_path)

# For convenience, also export these at module level
def _get_connector_video() -> Optional[str]:
    """Get the first available connector video"""
    processor = _get_default_processor()
    return processor._get_connector_video()

def _get_quiz_video() -> Optional[str]:
    """Get the first available quiz outro video"""
    processor = _get_default_processor()
    return processor._get_quiz_video()

# Module-level configuration variables for backward compatibility
USE_TRANSITIONS = True
TRANSITION_TYPE = DEFAULT_TRANSITION_TYPE
TRANSITION_DURATION = DEFAULT_TRANSITION_DURATION
FFMPEG_PRESET = DEFAULT_FFMPEG_PRESET