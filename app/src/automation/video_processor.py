# app/src/automation/video_processor.py
# Updated to support new asset structure and SVSL/VSL processing modes

import os
import shutil
import subprocess
import json
from typing import Optional, List, Tuple

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ASSETS_BASE_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos")

# Default settings
DEFAULT_TRANSITION_TYPE = "fade"
DEFAULT_TRANSITION_DURATION = 0.25
DEFAULT_FFMPEG_PRESET = "faster"

class VideoProcessor:
    """
    Video processor class for handling video concatenation with transitions
    Now supports new asset structure and SVSL/VSL modes
    """
    
    def __init__(self, use_transitions: bool = True, 
                 transition_type: str = DEFAULT_TRANSITION_TYPE,
                 transition_duration: float = DEFAULT_TRANSITION_DURATION,
                 account_code: str = None,
                 platform_code: str = None):
        """
        Initialize VideoProcessor with configuration
        
        Args:
            use_transitions: Whether to use transitions between videos
            transition_type: Type of transition (fade, slide, wipe, dissolve, etc.)
            transition_duration: Duration of transitions in seconds
            account_code: Account code (MCT, OO, etc.)
            platform_code: Platform code (FB, YT, REELS, etc.)
        """
        self.use_transitions = use_transitions
        self.transition_type = transition_type
        self.transition_duration = transition_duration
        self.ffmpeg_preset = DEFAULT_FFMPEG_PRESET
        
        # Store account and platform for asset path resolution
        self.account_code = account_code
        self.platform_code = platform_code
        
        print(f"🎬 VideoProcessor initialized")
        if self.account_code and self.platform_code:
            print(f"   📁 Account: {self.account_code}, Platform: {self.platform_code}")
        if self.use_transitions:
            print(f"   ✨ Transitions: {self.transition_type} ({self.transition_duration}s)")
    
    def set_account_platform(self, account_code: str, platform_code: str):
        """Update account and platform codes for asset path resolution"""
        self.account_code = account_code
        self.platform_code = platform_code
        print(f"📁 Updated: Account={account_code}, Platform={platform_code}")
    
    def _get_asset_path(self, asset_type: str) -> str:
        """
        Get the path to a specific asset type based on account and platform
        
        Args:
            asset_type: Type of asset (Connectors, Quiz, SVSL, VSL)
        
        Returns:
            Path to the asset directory
        """
        if not self.account_code or not self.platform_code:
            # Fallback to old structure if no account/platform set
            print(f"⚠️ No account/platform set, using legacy paths")
            if asset_type == "Connectors":
                return os.path.join(SCRIPT_DIR, "Assets", "Videos", "connectors")
            elif asset_type == "Quiz":
                return os.path.join(SCRIPT_DIR, "Assets", "Videos", "quiz_outro")
            else:
                return None
        
        # Build path based on new structure
        asset_path = os.path.join(ASSETS_BASE_PATH, self.account_code, self.platform_code, asset_type)
        
        # Check if path exists, if not try without platform for some assets
        if not os.path.exists(asset_path) and asset_type in ["SVSL", "VSL"]:
            # Try direct account level for SVSL/VSL if not platform-specific
            asset_path = os.path.join(ASSETS_BASE_PATH, self.account_code, asset_type)
        
        return asset_path if os.path.exists(asset_path) else None
    
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
            processing_mode: One of "connector_quiz", "quiz_only", "save_only",
                           "svsl_only", "connector_svsl", "vsl_only", "connector_vsl"
        
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
        
        # Process different modes
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
        
        elif processing_mode == "svsl_only":
            # Add only SVSL
            svsl = self._get_svsl_video()
            if svsl:
                video_list.append(svsl)
                print(f"✅ Added SVSL: {os.path.basename(svsl)}")
        
        elif processing_mode == "connector_svsl":
            # Add connector
            connector = self._get_connector_video()
            if connector:
                video_list.append(connector)
                print(f"✅ Added connector: {os.path.basename(connector)}")
            
            # Add SVSL
            svsl = self._get_svsl_video()
            if svsl:
                video_list.append(svsl)
                print(f"✅ Added SVSL: {os.path.basename(svsl)}")
        
        elif processing_mode == "vsl_only":
            # Add only VSL
            vsl = self._get_vsl_video()
            if vsl:
                video_list.append(vsl)
                print(f"✅ Added VSL: {os.path.basename(vsl)}")
        
        elif processing_mode == "connector_vsl":
            # Add connector
            connector = self._get_connector_video()
            if connector:
                video_list.append(connector)
                print(f"✅ Added connector: {os.path.basename(connector)}")
            
            # Add VSL
            vsl = self._get_vsl_video()
            if vsl:
                video_list.append(vsl)
                print(f"✅ Added VSL: {os.path.basename(vsl)}")
        
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
        connector_path = self._get_asset_path("Connectors")
        
        if not connector_path:
            print(f"⚠️ Connector directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(connector_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(connector_path, files[0])
        
        print(f"⚠️ No connector videos found in {connector_path}")
        return None
    
    def _get_quiz_video(self) -> Optional[str]:
        """Get the first available quiz outro video"""
        quiz_path = self._get_asset_path("Quiz")
        
        if not quiz_path:
            print(f"⚠️ Quiz outro directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(quiz_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(quiz_path, files[0])
        
        print(f"⚠️ No quiz outro videos found in {quiz_path}")
        return None
    
    def _get_svsl_video(self) -> Optional[str]:
        """Get the first available SVSL video"""
        svsl_path = self._get_asset_path("SVSL")
        
        if not svsl_path:
            print(f"⚠️ SVSL directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(svsl_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(svsl_path, files[0])
        
        print(f"⚠️ No SVSL videos found in {svsl_path}")
        return None
    
    def _get_vsl_video(self) -> Optional[str]:
        """Get the first available VSL video"""
        vsl_path = self._get_asset_path("VSL")
        
        if not vsl_path:
            print(f"⚠️ VSL directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(vsl_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(vsl_path, files[0])
        
        print(f"⚠️ No VSL videos found in {vsl_path}")
        return None
    
    def _fallback_concat(self, video_list: List[str], output_path: str, 
                        target_width: int, target_height: int) -> Optional[str]:
        """Simple concatenation without transitions using FFmpeg"""
        print(f"📹 Concatenating {len(video_list)} videos...")
        
        try:
            # Create temp file list for FFmpeg concat
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for video in video_list:
                    f.write(f"file '{video}'\n")
                list_file = f.name
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c:v', 'libx264',
                '-preset', self.ffmpeg_preset,
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2',
                output_path
            ]
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.unlink(list_file)
            
            if result.returncode == 0:
                print(f"✅ Video concatenation successful")
                return None
            else:
                return f"FFmpeg error: {result.stderr}"
                
        except Exception as e:
            return f"Concatenation failed: {e}"
    
    def configure_transitions(self, enabled: bool, transition_type: str = None, duration: float = None):
        """Update transition configuration"""
        self.use_transitions = enabled
        if transition_type:
            self.transition_type = transition_type
        if duration:
            self.transition_duration = duration
        print(f"✨ Transitions configured: {enabled}, Type: {self.transition_type}, Duration: {self.transition_duration}s")
    
    def get_video_dimensions(self, video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """Get video dimensions using ffprobe"""
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

def set_processor_account_platform(account_code: str, platform_code: str):
    """Set account and platform for the default processor"""
    processor = _get_default_processor()
    processor.set_account_platform(account_code, platform_code)

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
        processing_mode: One of "connector_quiz", "quiz_only", "save_only",
                        "svsl_only", "connector_svsl", "vsl_only", "connector_vsl"
    
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

def _get_svsl_video() -> Optional[str]:
    """Get the first available SVSL video"""
    processor = _get_default_processor()
    return processor._get_svsl_video()

def _get_vsl_video() -> Optional[str]:
    """Get the first available VSL video"""
    processor = _get_default_processor()
    return processor._get_vsl_video()

# Module-level configuration variables for backward compatibility
USE_TRANSITIONS = True
TRANSITION_TYPE = DEFAULT_TRANSITION_TYPE
TRANSITION_DURATION = DEFAULT_TRANSITION_DURATION
FFMPEG_PRESET = DEFAULT_FFMPEG_PRESET