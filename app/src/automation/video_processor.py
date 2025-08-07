# app/src/automation/video_processor.py
# Updated to use the new transitions module

import os
import shutil

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CONNECTORS_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "connectors")
QUIZ_OUTRO_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "quiz_outro")

# Transition settings (can be configured)
USE_TRANSITIONS = True
TRANSITION_TYPE = "fade"  # Options: fade, slide, wipe, dissolve, fadeblack, etc.
TRANSITION_DURATION = 0.5  # Duration in seconds

def process_video_sequence(client_video, output_path, target_width, target_height, 
                          processing_mode="connector_quiz"):
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
        connector = _get_connector_video()
        if connector:
            video_list.append(connector)
            print(f"✅ Added connector: {os.path.basename(connector)}")
        
        # Add quiz outro
        quiz = _get_quiz_video()
        if quiz:
            video_list.append(quiz)
            print(f"✅ Added quiz outro: {os.path.basename(quiz)}")
    
    elif processing_mode == "quiz_only":
        # Add only quiz outro
        quiz = _get_quiz_video()
        if quiz:
            video_list.append(quiz)
            print(f"✅ Added quiz outro: {os.path.basename(quiz)}")
    
    # Process with or without transitions
    if USE_TRANSITIONS and len(video_list) > 1:
        print(f"🎞️ Applying {TRANSITION_TYPE} transitions...")
        from .transitions import apply_transitions_to_video
        return apply_transitions_to_video(
            video_list, 
            output_path, 
            target_width, 
            target_height,
            TRANSITION_TYPE,
            TRANSITION_DURATION
        )
    else:
        # Use simple concatenation
        from .transitions.processor import TransitionProcessor
        processor = TransitionProcessor()
        return processor._fallback_concat(video_list, output_path, target_width, target_height)

def _get_connector_video():
    """Get the first available connector video"""
    if not os.path.exists(CONNECTORS_PATH):
        print(f"⚠️ Connector directory not found: {CONNECTORS_PATH}")
        return None
    
    files = [f for f in os.listdir(CONNECTORS_PATH) 
             if f.lower().endswith(('.mp4', '.mov'))]
    
    if files:
        return os.path.join(CONNECTORS_PATH, files[0])
    
    print(f"⚠️ No connector videos found")
    return None

def _get_quiz_video():
    """Get the first available quiz outro video"""
    if not os.path.exists(QUIZ_OUTRO_PATH):
        print(f"⚠️ Quiz outro directory not found: {QUIZ_OUTRO_PATH}")
        return None
    
    files = [f for f in os.listdir(QUIZ_OUTRO_PATH) 
             if f.lower().endswith(('.mp4', '.mov'))]
    
    if files:
        return os.path.join(QUIZ_OUTRO_PATH, files[0])
    
    print(f"⚠️ No quiz outro videos found")
    return None

def configure_transitions(enabled=True, transition_type="fade", duration=0.5):
    """
    Configure transition settings
    
    Args:
        enabled: Whether to use transitions
        transition_type: Type of transition to use
        duration: Transition duration in seconds
    """
    global USE_TRANSITIONS, TRANSITION_TYPE, TRANSITION_DURATION
    
    USE_TRANSITIONS = enabled
    TRANSITION_TYPE = transition_type
    TRANSITION_DURATION = max(0.25, min(2.0, duration))
    
    print(f"✅ Transitions configured:")
    print(f"   Enabled: {USE_TRANSITIONS}")
    print(f"   Type: {TRANSITION_TYPE}")
    print(f"   Duration: {TRANSITION_DURATION}s")

# For backward compatibility
def get_video_dimensions(video_path):
    """Get video dimensions (for backward compatibility)"""
    from .transitions.video_info import VideoInfo
    width, height = VideoInfo.get_dimensions(video_path)
    if width and height:
        return width, height, None
    return None, None, "Could not get video dimensions"