# app/src/automation/transitions/transition_types.py
"""
Defines available transition types and their configurations
"""

from enum import Enum

class TransitionType(Enum):
    """Available transition types"""
    FADE = "fade"
    SLIDE = "slide"
    WIPE = "wipe"
    DISSOLVE = "dissolve"
    FADEBLACK = "fadeblack"
    FADEGRAYS = "fadegrays"
    DISTANCE = "distance"
    SMOOTHLEFT = "smoothleft"
    SMOOTHRIGHT = "smoothright"
    CIRCLEOPEN = "circleopen"
    CIRCLECLOSE = "circleclose"

# Transition configurations
TRANSITION_CONFIGS = {
    "fade": {
        "ffmpeg_name": "fade",
        "default_duration": 0.5,
        "audio_curve": "tri",
        "description": "Smooth crossfade between videos"
    },
    "slide": {
        "ffmpeg_name": "slideleft",
        "default_duration": 0.7,
        "audio_curve": "tri",
        "description": "Slide transition from right to left"
    },
    "wipe": {
        "ffmpeg_name": "wipeleft",
        "default_duration": 0.6,
        "audio_curve": "qsin",
        "description": "Wipe transition from right to left"
    },
    "dissolve": {
        "ffmpeg_name": "dissolve",
        "default_duration": 0.5,
        "audio_curve": "exp",
        "description": "Dissolve effect between videos"
    },
    "fadeblack": {
        "ffmpeg_name": "fadeblack",
        "default_duration": 0.4,
        "audio_curve": "tri",
        "description": "Fade through black"
    },
    "fadegrays": {
        "ffmpeg_name": "fadegrays",
        "default_duration": 0.5,
        "audio_curve": "tri",
        "description": "Fade through grayscale"
    },
    "smoothleft": {
        "ffmpeg_name": "smoothleft",
        "default_duration": 0.8,
        "audio_curve": "tri",
        "description": "Smooth slide to the left"
    },
    "smoothright": {
        "ffmpeg_name": "smoothright",
        "default_duration": 0.8,
        "audio_curve": "tri",
        "description": "Smooth slide to the right"
    },
    "circleopen": {
        "ffmpeg_name": "circleopen",
        "default_duration": 0.6,
        "audio_curve": "qsin",
        "description": "Circle opening transition"
    },
    "circleclose": {
        "ffmpeg_name": "circleclose",
        "default_duration": 0.6,
        "audio_curve": "qsin",
        "description": "Circle closing transition"
    }
}

def get_transition_config(transition_type):
    """Get configuration for a transition type"""
    if isinstance(transition_type, TransitionType):
        transition_type = transition_type.value
    
    return TRANSITION_CONFIGS.get(
        transition_type, 
        TRANSITION_CONFIGS["fade"]  # Default to fade
    )