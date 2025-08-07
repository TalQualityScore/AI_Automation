# app/src/automation/transitions/processor.py
"""
Main processor that applies transitions to video sequences
"""

import os
import sys
import subprocess
from .video_info import VideoInfo
from .transition_builder import TransitionBuilder

class TransitionProcessor:
    """Processes videos with transitions"""
    
    def __init__(self, transition_type="fade", duration=None):
        self.transition_type = transition_type
        self.duration = duration
        self.builder = TransitionBuilder(transition_type, duration)
    
    def process(self, video_list, output_path, width, height):
        """
        Process video list with transitions
        
        Returns:
            None on success, error message on failure
        """
        if len(video_list) == 0:
            return "No videos to process"
        
        if len(video_list) == 1:
            return self._process_single(video_list[0], output_path, width, height)
        
        # Get video durations
        durations = []
        for video in video_list:
            duration = VideoInfo.get_duration(video)
            if duration <= 0:
                print(f"⚠️ Could not get duration for {os.path.basename(video)}")
                return self._fallback_concat(video_list, output_path, width, height)
            durations.append(duration)
        
        # Apply transitions
        return self._apply_transitions(video_list, durations, output_path, width, height)
    
    def _process_single(self, video_path, output_path, width, height):
        """Process single video (no transitions needed)"""
        command = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
                   f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-movflags', '+faststart',
            output_path
        ]
        
        return self._run_ffmpeg(command)
    
    def _apply_transitions(self, video_list, durations, output_path, width, height):
        """Apply transitions between videos"""
        
        # Build FFmpeg command
        command = ['ffmpeg', '-y']
        
        # Add input files
        for video in video_list:
            command.extend(['-i', video])
        
        # Build filter complex
        filters = []
        
        # Normalize all videos first
        filters.extend(
            self.builder.build_normalization_filters(len(video_list), width, height)
        )
        
        # Add transitions
        if len(video_list) == 2:
            offset = durations[0] - self.builder.duration
            filters.extend(self.builder.build_two_video_transition(offset))
        else:
            filters.extend(self.builder.build_multi_video_transitions(durations))
        
        # Combine filters
        filter_complex = "".join(filters)
        
        command.extend([
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-movflags', '+faststart',
            output_path
        ])
        
        error = self._run_ffmpeg(command)
        
        if error:
            print(f"⚠️ Transition failed, falling back to simple concat")
            return self._fallback_concat(video_list, output_path, width, height)
        
        return None
    
    def _fallback_concat(self, video_list, output_path, width, height):
        """Fallback to simple concatenation without transitions"""
        print("🔄 Using simple concatenation (no transitions)")
        
        command = ['ffmpeg', '-y']
        
        # Add input files
        for video in video_list:
            command.extend(['-i', video])
        
        # Build filter complex
        filters = self.builder.build_normalization_filters(len(video_list), width, height)
        filters.extend(self.builder.build_simple_concat(len(video_list)))
        
        filter_complex = "".join(filters)
        
        command.extend([
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-c:a', 'aac',
            output_path
        ])
        
        return self._run_ffmpeg(command)
    
    def _run_ffmpeg(self, command):
        """Run FFmpeg command with proper error handling"""
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes
                startupinfo=startupinfo
            )
            
            if result.returncode == 0:
                print("✅ Processing successful")
                return None
            else:
                return f"FFmpeg error: {result.stderr[:500]}"  # Limit error message length
                
        except subprocess.TimeoutExpired:
            return "Processing timed out after 30 minutes"
        except Exception as e:
            return f"Processing error: {e}"