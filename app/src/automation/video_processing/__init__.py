# app/src/automation/video_processing/__init__.py
"""
Video Processing Modules
Organized components for video processing operations
"""

from .video_analyzer import VideoAnalyzer, set_fallback_dimensions, get_fallback_dimensions, get_video_dimensions_with_fallback
from .asset_manager import AssetManager
from .concat_processor import ConcatProcessor
from .transition_processor import TransitionProcessor
from .processor_config import ProcessorConfig

__all__ = [
    'VideoAnalyzer',
    'AssetManager',
    'ConcatProcessor',
    'TransitionProcessor',
    'ProcessorConfig',
    'set_fallback_dimensions',
    'get_fallback_dimensions',
    'get_video_dimensions_with_fallback'
]