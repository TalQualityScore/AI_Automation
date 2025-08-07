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
        """Apply transitions between videos with SFX"""
        
        import os
        import shutil
        
        # Check for SFX file
        sfx_path = self._get_sfx_path()
        has_sfx = sfx_path and os.path.exists(sfx_path)
        
        # Build FFmpeg command
        command = ['ffmpeg', '-y']
        
        # Add input files
        for video in video_list:
            command.extend(['-i', video])
        
        # Add SFX for each transition if available
        if has_sfx:
            num_transitions = len(video_list) - 1
            for _ in range(num_transitions):
                command.extend(['-i', sfx_path])
        
        # Build filter complex
        filters = []
        
        # Normalize all videos first
        filters.extend(
            self.builder.build_normalization_filters(len(video_list), width, height)
        )
        
        # Add transitions (video only) and handle audio
        if len(video_list) == 2:
            offset = durations[0] - self.builder.duration
            filters.extend(self.builder.build_video_only_transition_with_sfx(
                offset, has_sfx, len(video_list)
            ))
        else:
            filters.extend(self.builder.build_multi_video_transitions_with_sfx(
                durations, has_sfx, len(video_list)
            ))
        
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
        
        # Copy SFX to project folder if successful
        if not error and has_sfx:
            self._copy_sfx_to_project(sfx_path, output_path)
        
        return None
    
    def _get_sfx_path(self):
        """Get the path to fadeout SFX"""
        import os
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )))
        sfx_dir = os.path.join(script_dir, "Assets", "Audio", "SFX")
        
        # Look for fadeout_sfx file (with any extension)
        if os.path.exists(sfx_dir):
            for file in os.listdir(sfx_dir):
                if file.lower().startswith('fadeout_sfx'):
                    sfx_path = os.path.join(sfx_dir, file)
                    print(f"✅ Found SFX: {file}")
                    return sfx_path
        
        print(f"⚠️ No fadeout_sfx found in {sfx_dir}")
        return None
    
    def _copy_sfx_to_project(self, sfx_path, output_path):
        """Copy SFX to project's Audio/SFX folder"""
        import os
        import shutil
        
        # Get project folder from output path
        project_folder = os.path.dirname(os.path.dirname(output_path))
        audio_sfx_folder = os.path.join(project_folder, "_Audio", "SFX")
        
        if os.path.exists(audio_sfx_folder):
            try:
                dest_path = os.path.join(audio_sfx_folder, os.path.basename(sfx_path))
                shutil.copy2(sfx_path, dest_path)
                print(f"✅ Copied SFX to project: {dest_path}")
            except Exception as e:
                print(f"⚠️ Could not copy SFX to project: {e}")
    
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