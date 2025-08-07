# app/src/automation/transitions/__init__.py
"""
Video Transitions Module
Handles smooth transitions between video segments
"""

from .transition_types import TransitionType, TRANSITION_CONFIGS
from .transition_builder import TransitionBuilder
from .video_info import VideoInfo
from .processor import TransitionProcessor

__all__ = [
    'TransitionType',
    'TransitionBuilder', 
    'VideoInfo',
    'TransitionProcessor',
    'apply_transitions_to_video'
]

def apply_transitions_to_video(video_list, output_path, width, height, 
                              transition_type="fade", duration=0.5):
    """
    Simple interface to apply transitions to videos
    
    Args:
        video_list: List of video file paths
        output_path: Output file path
        width: Target width
        height: Target height
        transition_type: Type of transition (fade, slide, wipe, etc.)
        duration: Transition duration in seconds
    
    Returns:
        None on success, error message on failure
    """
    processor = TransitionProcessor(transition_type, duration)
    return processor.process(video_list, output_path, width, height)