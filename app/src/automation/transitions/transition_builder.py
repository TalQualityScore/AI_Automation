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
    
    def build_video_only_transition_with_sfx(self, offset, has_sfx=False, num_videos=2):
        """
        Build transition for video only (keep audio continuous) with optional SFX
        
        Args:
            offset: Transition start time
            has_sfx: Whether SFX is available
            num_videos: Number of main videos
        """
        filters = []
        
        # Video transition (fade only video, not audio)
        video_filter = (
            f"[v0][v1]xfade=transition={self.config['ffmpeg_name']}:"
            f"duration={self.duration}:offset={offset}[vout];"
        )
        filters.append(video_filter)
        
        if has_sfx:
            # Mix SFX with original audio
            # SFX is at index num_videos (after all video inputs)
            sfx_index = num_videos
            
            # Trim and fade SFX to match transition duration
            filters.append(
                f"[{sfx_index}:a]atrim=0:{self.duration},"
                f"afade=t=in:d=0.1,"
                f"afade=t=out:st={self.duration-0.1}:d=0.1,"
                f"volume=0.4[sfx];"  # 40% volume
            )
            
            # Delay SFX to start at transition point
            filters.append(
                f"[sfx]adelay={int(offset*1000)}|{int(offset*1000)}[sfx_delayed];"
            )
            
            # Keep original audio continuous (no crossfade)
            filters.append(
                f"[a0][a1]concat=n=2:v=0:a=1[main_audio];"
            )
            
            # Mix main audio with SFX
            filters.append(
                f"[main_audio][sfx_delayed]amix=inputs=2:duration=longest[aout]"
            )
        else:
            # No SFX, just concatenate audio without crossfade
            filters.append(
                f"[a0][a1]concat=n=2:v=0:a=1[aout]"
            )
        
        return filters
    
    def build_multi_video_transitions_with_sfx(self, video_durations, has_sfx=False, num_videos=None):
        """
        Build transitions for 3+ videos with video-only fade and optional SFX
        
        Args:
            video_durations: List of video durations
            has_sfx: Whether SFX is available
            num_videos: Number of main videos
        """
        filters = []
        current_video = "v0"
        num_vids = num_videos or len(video_durations)
        
        # Build video transitions
        for i in range(1, len(video_durations)):
            # Calculate offset for this transition
            total_duration = sum(video_durations[:i])
            offset = total_duration - (self.duration * i)
            
            # Determine output names
            is_last = (i == len(video_durations) - 1)
            output_video = "vout" if is_last else f"vtrans{i}"
            
            # Video transition only
            filters.append(
                f"[{current_video}][v{i}]xfade=transition={self.config['ffmpeg_name']}:"
                f"duration={self.duration}:offset={offset}[{output_video}];"
            )
            
            current_video = output_video
        
        # Handle audio separately
        if has_sfx:
            # Process each SFX for each transition
            sfx_outputs = []
            for i in range(len(video_durations) - 1):
                sfx_index = num_vids + i  # SFX inputs come after videos
                total_duration = sum(video_durations[:i+1])
                offset = total_duration - (self.duration * (i+1))
                
                # Process SFX
                filters.append(
                    f"[{sfx_index}:a]atrim=0:{self.duration},"
                    f"afade=t=in:d=0.1,"
                    f"afade=t=out:st={self.duration-0.1}:d=0.1,"
                    f"volume=0.4,"  # 40% volume
                    f"adelay={int(offset*1000)}|{int(offset*1000)}[sfx{i}];"
                )
                sfx_outputs.append(f"[sfx{i}]")
            
            # Concatenate all main audio
            audio_concat = ""
            for i in range(len(video_durations)):
                audio_concat += f"[a{i}]"
            filters.append(
                f"{audio_concat}concat=n={len(video_durations)}:v=0:a=1[main_audio];"
            )
            
            # Mix all SFX with main audio
            all_inputs = "[main_audio]" + "".join(sfx_outputs)
            filters.append(
                f"{all_inputs}amix=inputs={1 + len(sfx_outputs)}:duration=longest[aout]"
            )
        else:
            # No SFX, just concatenate audio
            audio_concat = ""
            for i in range(len(video_durations)):
                audio_concat += f"[a{i}]"
            filters.append(
                f"{audio_concat}concat=n={len(video_durations)}:v=0:a=1[aout]"
            )
        
        return filters
    
    def build_simple_concat(self, num_videos):
        """Build simple concatenation filter (no transitions)"""
        concat_inputs = ""
        for i in range(num_videos):
            concat_inputs += f"[v{i}][a{i}]"
        
        return [f"{concat_inputs}concat=n={num_videos}:v=1:a=1[vout][aout]"]
    
    # Keep old methods for backward compatibility
    def build_two_video_transition(self, offset):
        """Legacy method - redirects to new video-only transition"""
        return self.build_video_only_transition_with_sfx(offset, has_sfx=False, num_videos=2)
    
    def build_multi_video_transitions(self, video_durations):
        """Legacy method - redirects to new video-only transitions"""
        return self.build_multi_video_transitions_with_sfx(video_durations, has_sfx=False)