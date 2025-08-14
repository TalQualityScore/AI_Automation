# app/src/automation/video_processor.py - REFACTORED
"""
Video Processor - REFACTORED
Main interface that uses modular components
"""

import os
import shutil
from typing import Optional, List, Tuple, Dict
from .video_processing import (
    VideoAnalyzer, AssetManager, ConcatProcessor,
    TransitionProcessor, ProcessorConfig,
    # NEW: Import fallback functions
    set_fallback_dimensions, get_fallback_dimensions, 
    get_video_dimensions_with_fallback
)

class VideoProcessor:
    """
    Main video processor class - now uses modular components
    Reduced from 650+ lines to ~150 lines
    """
    
    def __init__(self, use_transitions: bool = True,
                transition_type: str = None,
                transition_duration: float = None,
                account_code: str = None,
                platform_code: str = None):
        """Initialize VideoProcessor with modular components"""
        
        # Initialize configuration
        self.config = ProcessorConfig()
        
        # FORCE HIGHER LIMIT FOR TESTING:
        self.config.TRANSITION_MAX_DURATION = 5400  # 90 minutes
        
        # Initialize modules
        self.analyzer = VideoAnalyzer()
        self.asset_manager = AssetManager(account_code, platform_code)
        self.concat_processor = ConcatProcessor()
        self.transition_processor = TransitionProcessor()
        
        # Settings - ENSURE TRANSITIONS ARE ON
        self.use_transitions = True  # Force True for testing
        self.transition_type = transition_type or self.config.DEFAULT_TRANSITION_TYPE
        self.transition_duration = transition_duration or self.config.DEFAULT_TRANSITION_DURATION
        
        print(f"🎬 VideoProcessor initialized (Modular Version)")
        print(f"   ✨ TRANSITIONS FORCED ON")
        print(f"   ✨ Max duration: {self.config.TRANSITION_MAX_DURATION}s")
        if account_code and platform_code:
            print(f"   📁 Account: {account_code}, Platform: {platform_code}")
        if self.use_transitions:
            print(f"   ✨ Transitions: {self.transition_type} ({self.transition_duration}s)")
    
    def set_account_platform(self, account_code: str, platform_code: str):
        """Update account and platform codes"""
        self.asset_manager.set_account_platform(account_code, platform_code)
    
    def process_video_sequence(self, client_video: str, output_path: str,
                            target_width: int, target_height: int,
                            processing_mode: str = "connector_quiz") -> Optional[str]:
        """Process video sequence with specified mode"""
        print(f"🎬 Starting video processing in {processing_mode} mode...")
        
        # Handle save_only mode
        if processing_mode == "save_only":
            try:
                shutil.copy2(client_video, output_path)
                print(f"✅ Video copied successfully")
                return None
            except Exception as e:
                return f"Copy failed: {e}"
        
        # Build video list based on processing mode
        video_list = self._build_video_list(client_video, processing_mode)
        
        # Determine target specs
        target_specs = self.analyzer.determine_target_specs(video_list)
        
        # ADD THESE DEBUG LINES:
        print(f"🔍 DEBUG TRANSITIONS:")
        print(f"   - Total duration: {target_specs.get('total_duration', 0):.1f}s")
        print(f"   - Max allowed for transitions: {self.config.TRANSITION_MAX_DURATION}s")
        print(f"   - Transitions enabled: {self.use_transitions}")
        print(f"   - Video count: {len(video_list)}")
        print(f"   - Video list: {[os.path.basename(v) for v in video_list]}")
        
        # Process based on duration and settings
        should_use = self._should_use_transitions(video_list, target_specs)
        print(f"   - Should use transitions: {should_use}")
        
        if should_use:
            print("✅ APPLYING TRANSITIONS!")
            return self.transition_processor.apply_transitions(
                video_list, output_path, target_specs,
                self.transition_type, self.transition_duration
            )
        else:
            print("❌ NOT USING TRANSITIONS - Using concat")
            return self.concat_processor.robust_concat(
                video_list, output_path, target_specs
            )
    
    def _build_video_list(self, client_video: str, processing_mode: str) -> List[str]:
        """Build list of videos based on processing mode"""
        video_list = [client_video]
        
        mode_mappings = {
            "connector_quiz": ["connector", "quiz"],
            "quiz_only": ["quiz"],
            "connector_svsl": ["connector", "svsl"],
            "svsl_only": ["svsl"],
            "connector_vsl": ["connector", "vsl"],
            "vsl_only": ["vsl"]
        }
        
        assets_to_add = mode_mappings.get(processing_mode, [])
        
        for asset_type in assets_to_add:
            video = self._get_asset_video(asset_type)
            if video:
                video_list.append(video)
                print(f"✅ Added {asset_type}: {os.path.basename(video)}")
        
        return video_list
    
    def _get_asset_video(self, asset_type: str) -> Optional[str]:
        """Get asset video by type"""
        asset_getters = {
            "connector": self.asset_manager.get_connector_video,
            "quiz": self.asset_manager.get_quiz_video,
            "svsl": self.asset_manager.get_svsl_video,
            "vsl": self.asset_manager.get_vsl_video
        }
        
        getter = asset_getters.get(asset_type)
        return getter() if getter else None
    
    def _should_use_transitions(self, video_list: List[str], specs: Dict) -> bool:
        """Determine whether to use transitions or robust concat"""
        if not self.use_transitions:
            print("❌ Transitions disabled in settings")
            return False
        
        if len(video_list) <= 1:
            print("❌ Single video - no transitions needed")
            return False
        
        # FIXED: Respect user's explicit transition choice for VSL and long videos
        TRANSITION_MAX_DURATION = 600  # 10 minutes default threshold
        
        print(f"🔍 DEBUG: Video duration: {specs['total_duration']:.1f}s, Max for transitions: {TRANSITION_MAX_DURATION}s")
        print(f"🔍 DEBUG: Transitions enabled: {self.use_transitions}")
        
        # If user explicitly enabled transitions, respect their choice even for long videos
        if self.use_transitions:
            if specs['total_duration'] < TRANSITION_MAX_DURATION:
                print("✅ 🎞️ Using TRANSITIONS for video sequence (normal duration)")
                return True
            else:
                print("✅ 🎞️ Using TRANSITIONS for LONG video sequence (user enabled)")
                print("⚠️ Processing may take longer due to video length")
                return True
        else:
            print("🔇 Transitions disabled by user - using robust concatenation")
            return False
    
    def configure_transitions(self, enabled: bool, transition_type: str = None,
                            duration: float = None):
        """Update transition configuration"""
        self.use_transitions = enabled
        if transition_type:
            self.transition_type = transition_type
        if duration:
            self.transition_duration = duration
        print(f"✨ Transitions configured: {enabled}, Type: {self.transition_type}, Duration: {self.transition_duration}s")
    
    def get_video_dimensions(self, video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """Get video dimensions"""
        return self.analyzer.get_video_dimensions(video_path)
    
    def validate_video_file(self, file_path: str) -> bool:
        """Validate if file is a supported video format"""
        return self.analyzer.validate_video_file(file_path)

# ============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# ============================================================================

# Global instance for backward compatibility
_default_processor = None

def _get_default_processor() -> VideoProcessor:
    """Get or create default processor instance"""
    global _default_processor
    if _default_processor is None:
        # FORCE TRANSITIONS ON WHEN CREATING DEFAULT PROCESSOR
        _default_processor = VideoProcessor(
            use_transitions=True,  # Force True
            transition_type="fade",
            transition_duration=0.5
        )
        print("🔍 DEBUG: Created default processor with transitions ENABLED")
    return _default_processor


def set_processor_account_platform(account_code: str, platform_code: str):
    """Set account and platform for the default processor"""
    processor = _get_default_processor()
    processor.set_account_platform(account_code, platform_code)

def process_video_sequence(client_video: str, output_path: str,
                          target_width: int, target_height: int,
                          processing_mode: str = "connector_quiz") -> Optional[str]:
    """Backward compatibility wrapper"""
    processor = _get_default_processor()
    return processor.process_video_sequence(
        client_video, output_path, target_width, target_height, processing_mode
    )

def configure_transitions(enabled: bool = True,
                        transition_type: str = "fade",
                        duration: float = 0.25):
    """Backward compatibility wrapper"""
    processor = _get_default_processor()
    processor.configure_transitions(enabled, transition_type, duration)

def get_video_dimensions(video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """Backward compatibility wrapper"""
    processor = _get_default_processor()
    return processor.get_video_dimensions(video_path)

# Legacy function exports for compatibility
def _get_connector_video() -> Optional[str]:
    processor = _get_default_processor()
    return processor.asset_manager.get_connector_video()

def _get_quiz_video() -> Optional[str]:
    processor = _get_default_processor()
    return processor.asset_manager.get_quiz_video()

def _get_svsl_video() -> Optional[str]:
    processor = _get_default_processor()
    return processor.asset_manager.get_svsl_video()

def _get_vsl_video() -> Optional[str]:
    processor = _get_default_processor()
    return processor.asset_manager.get_vsl_video()

__all__ = [
    'VideoProcessor',
    'set_processor_account_platform',
    'process_video_sequence', 
    'configure_transitions',
    'get_video_dimensions',
    # NEW: Export fallback functions
    'set_fallback_dimensions',
    'get_fallback_dimensions',
    'get_video_dimensions_with_fallback'
]