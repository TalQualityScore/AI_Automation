# app/src/automation/video_processing/processor_config.py
"""
Processor Configuration Module
Contains all configuration constants and settings
"""

import os

class ProcessorConfig:
    """Configuration constants for video processing"""
    
    # Paths
    SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    ASSETS_BASE_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos")
    
    # Default settings
    DEFAULT_TRANSITION_TYPE = "fade"
    DEFAULT_TRANSITION_DURATION = 0.25
    DEFAULT_FFMPEG_PRESET = "faster"
    
    # Video defaults
    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080
    DEFAULT_FRAME_RATE = 30.0
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_AUDIO_BITRATE = "192k"
    DEFAULT_VIDEO_CRF = 23
    
    # Processing thresholds
    TRANSITION_MAX_DURATION = 300  # 5 minutes - use transitions for videos shorter than this
    LONG_VIDEO_THRESHOLD = 1200    # 20 minutes
    VERY_LONG_VIDEO_THRESHOLD = 2400  # 40 minutes
    
    # Supported formats
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    
    @classmethod
    def get_preset_for_duration(cls, duration_seconds):
        """Get appropriate preset based on video duration"""
        if duration_seconds > cls.VERY_LONG_VIDEO_THRESHOLD:
            return 'faster'
        elif duration_seconds > cls.LONG_VIDEO_THRESHOLD:
            return 'medium'
        else:
            return 'medium'  # Prefer quality for shorter videos