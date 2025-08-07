# app/src/automation/transitions/transition_builder.py
"""
Builds FFmpeg filter complex for transitions
"""

from .transition_types import get_transition_config

class TransitionBuilder:
    """Builds FFmpeg filter strings for transitions"""
    
    def __init__(self, transition_type="fade", duration=None):
        self.config = get_transition_config(transition_type)
        self.duration = duration or self.config["default_duration"]
        # Clamp duration between reasonable values
        self.duration = max(0.25, min(2.0, self.duration))
    
    def build_normalization_filters(self, num_videos, width, height, fps=30, audio_rate=44100):
        """
        Build filters to normalize all input videos
        
        Returns:
            list: Filter strings for video and audio normalization
        """
        filters = []
        
        for i in range(num_videos):
            # Video normalization
            filters.append(
                f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                f"setsar=1,fps={fps}[v{i}];"
            )
            # Audio normalization
            filters.append(
                f"[{i}:a]aformat=sample_rates={audio_rate}:channel_layouts=stereo[a{i}];"
            )
        
        return filters
    
    def build_two_video_transition(self, offset):
        """Build transition between exactly 2 videos"""
        video_filter = (
            f"[v0][v1]xfade=transition={self.config['ffmpeg_name']}:"
            f"duration={self.duration}:offset={offset}[vout];"
        )
        
        audio_filter = (
            f"[a0][a1]acrossfade=d={self.duration}:"
            f"c1={self.config['audio_curve']}:c2={self.config['audio_curve']}[aout]"
        )
        
        return [video_filter, audio_filter]
    
    def build_multi_video_transitions(self, video_durations):
        """
        Build transitions for 3+ videos
        
        Args:
            video_durations: List of video durations in seconds
            
        Returns:
            list: Filter strings for all transitions
        """
        filters = []
        current_video = "v0"
        current_audio = "a0"
        
        for i in range(1, len(video_durations)):
            # Calculate offset for this transition
            total_duration = sum(video_durations[:i])
            offset = total_duration - (self.duration * i)
            
            # Determine output names
            is_last = (i == len(video_durations) - 1)
            output_video = "vout" if is_last else f"vtrans{i}"
            output_audio = "aout" if is_last else f"atrans{i}"
            
            # Video transition
            filters.append(
                f"[{current_video}][v{i}]xfade=transition={self.config['ffmpeg_name']}:"
                f"duration={self.duration}:offset={offset}[{output_video}];"
            )
            
            # Audio crossfade
            filters.append(
                f"[{current_audio}][a{i}]acrossfade=d={self.duration}:"
                f"c1={self.config['audio_curve']}:c2={self.config['audio_curve']}[{output_audio}];"
            )
            
            current_video = output_video
            current_audio = output_audio
        
        return filters
    
    def build_simple_concat(self, num_videos):
        """Build simple concatenation filter (no transitions)"""
        concat_inputs = ""
        for i in range(num_videos):
            concat_inputs += f"[v{i}][a{i}]"
        
        return [f"{concat_inputs}concat=n={num_videos}:v=1:a=1[vout][aout]"]