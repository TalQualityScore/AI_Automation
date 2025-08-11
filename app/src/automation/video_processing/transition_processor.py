# app/src/automation/video_processing/transition_processor.py - FIXED VERSION
"""
Transition Processor Module - FIXED
Handles video transitions (crossfade, fade, etc.) with proper timing
"""

import subprocess
from typing import List, Dict, Optional
from .processor_config import ProcessorConfig
from .video_analyzer import VideoAnalyzer

class TransitionProcessor:
    """Handles video transitions between segments"""
    
    def __init__(self):
        self.config = ProcessorConfig()
        self.analyzer = VideoAnalyzer()
    
    def apply_transitions(self, video_list: List[str], output_path: str, 
                         specs: Dict, transition_type: str = "fade",
                         duration: float = 0.5) -> Optional[str]:
        """Apply transitions between videos"""
        
        if len(video_list) == 1:
            # No transitions needed for single video
            from .concat_processor import ConcatProcessor
            concat = ConcatProcessor()
            return concat.robust_concat(video_list, output_path, specs)
        
        print(f"🎞️ TRANSITIONS: Processing {len(video_list)} videos with {transition_type} transitions...")
        
        try:
            if len(video_list) == 2:
                return self._apply_two_video_transition(
                    video_list, output_path, specs, transition_type, duration
                )
            elif len(video_list) == 3:
                return self._apply_three_video_transition(
                    video_list, output_path, specs, transition_type, duration
                )
            else:
                # For 4+ videos, use robust concat for now
                print("⚠️ 4+ videos detected, using robust concat instead of transitions")
                from .concat_processor import ConcatProcessor
                concat = ConcatProcessor()
                return concat.robust_concat(video_list, output_path, specs)
                
        except Exception as e:
            print(f"⚠️ Transitions error: {e}")
            print("🔄 Using robust concat fallback")
            from .concat_processor import ConcatProcessor
            concat = ConcatProcessor()
            return concat.robust_concat(video_list, output_path, specs)
    
    # In app/src/automation/video_processing/transition_processor.py
    def _apply_two_video_transition(self, video_list: List[str], output_path: str,
                                   specs: Dict, transition_type: str,
                                   duration: float) -> Optional[str]:
        """Apply transition with PERFECT AUDIO SYNC - FIXED VERSION"""
        
        # Get durations
        first_video_info = self.analyzer.get_video_info(video_list[0])
        second_video_info = self.analyzer.get_video_info(video_list[1])
        
        first_duration = first_video_info.get('duration', 10)
        second_duration = second_video_info.get('duration', 10)
        
        # Use 0.25s transition
        trans_duration = 0.25
        
        # Calculate precise transition point
        transition_start = first_duration - trans_duration
        
        print(f"   📍 Video 1: {first_duration:.2f}s")
        print(f"   📍 Video 2: {second_duration:.2f}s")
        print(f"   📍 Transition: {transition_start:.2f}s for {trans_duration}s")
        
        # CRITICAL AUDIO SYNC FIX: Process audio and video separately
        filter_complex = (
            # Process videos
            f"[0:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1[v0];"
            
            f"[1:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1[v1];"
            
            # Apply video crossfade
            f"[v0][v1]xfade=transition=fade:duration={trans_duration}:offset={transition_start}[vout];"
            
            # AUDIO FIX: Split and concat at exact point
            # Take first audio until transition point
            f"[0:a]atrim=0:{transition_start},asetpts=PTS-STARTPTS[a0_part];"
            
            # Take second audio completely
            f"[1:a]asetpts=PTS-STARTPTS[a1_part];"
            
            # Normalize both parts
            f"[a0_part]aresample={specs['sample_rate']}:async=1,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a0_norm];"
            
            f"[a1_part]aresample={specs['sample_rate']}:async=1,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a1_norm];"
            
            # Concatenate audio parts
            f"[a0_norm][a1_norm]concat=n=2:v=0:a=1[aout]"
        )
        
        # Build command
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
            '-i', video_list[0],
            '-i', video_list[1],
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-preset', specs.get('preset', 'medium'),
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', str(specs['sample_rate']),
            '-ac', '2',
            output_path
        ]
        
        print("🎬 Applying transition with audio sync fix...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Transition applied successfully")
            return None
        else:
            print(f"⚠️ Transition failed: {result.stderr[:500]}")
            # Fallback to simple concat
            return self._concat_with_simple_cut(video_list, output_path, specs)
    
    def _concat_with_simple_cut(self, video_list: List[str], output_path: str, specs: Dict) -> Optional[str]:
        """Fallback: Simple concatenation with cut instead of crossfade"""
        print("🔄 Using simple cut (no transition) to ensure perfect sync")
        
        from .concat_processor import ConcatProcessor
        concat = ConcatProcessor()
        return concat.robust_concat(video_list, output_path, specs)
    
    def _apply_three_video_transition(self, video_list: List[str], output_path: str,
                                     specs: Dict, transition_type: str,
                                     duration: float) -> Optional[str]:
        """Apply transitions between three videos - NEW"""
        
        # Get durations
        first_info = self.analyzer.get_video_info(video_list[0])
        second_info = self.analyzer.get_video_info(video_list[1])
        
        first_duration = first_info.get('duration', 10)
        second_duration = second_info.get('duration', 10)
        
        # Calculate transition points
        trans1_start = max(0, first_duration - 1.0)
        trans2_start = max(0, first_duration + second_duration - 2.0)
        actual_duration = 0.5
        
        print(f"   📍 Video 1 duration: {first_duration:.1f}s")
        print(f"   📍 Video 2 duration: {second_duration:.1f}s")
        print(f"   📍 Transition 1 at: {trans1_start:.1f}s")
        print(f"   📍 Transition 2 at: {trans2_start:.1f}s")
        
        # Build complex filter for 3 videos
        filter_complex = self._build_three_video_filter(
            specs, trans1_start, trans2_start, actual_duration
        )
        
        cmd = [
            'ffmpeg', '-y', '-hide_banner',
            '-i', video_list[0],
            '-i', video_list[1],
            '-i', video_list[2],
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-preset', specs.get('preset', 'medium'),
            '-crf', str(self.config.DEFAULT_VIDEO_CRF),
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', self.config.DEFAULT_AUDIO_BITRATE,
            '-ar', str(specs['sample_rate']),
            '-movflags', '+faststart',
            output_path
        ]
        
        print("🎬 Applying crossfade transitions (3 videos)...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Transitions applied successfully")
            return None
        else:
            print(f"⚠️ Transitions failed, using concat: {result.stderr[:200]}")
            from .concat_processor import ConcatProcessor
            concat = ConcatProcessor()
            return concat.robust_concat(video_list, output_path, specs)
        
    
    def _build_crossfade_filter(self, specs: Dict, transition_start: float, 
                            duration: float) -> str:
        """Build crossfade transition filter with PERFECT audio sync"""
        
        # Calculate exact offset to prevent audio drift
        offset = transition_start
        
        return (
            # Prepare videos with identical specs
            f"[0:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1[v0];"
            
            f"[1:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1[v1];"
            
            # CRITICAL: Fix audio sync with proper PTS alignment
            f"[0:a]aresample={specs['sample_rate']}:async=1:first_pts=0,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a0];"
            
            f"[1:a]aresample={specs['sample_rate']}:async=1:first_pts=0,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo,"
            f"adelay={int(offset*1000)}|{int(offset*1000)}[a1_delayed];"
            
            # Video crossfade
            f"[v0][v1]xfade=transition=fade:duration={duration}:offset={offset}[vout];"
            
            # Audio: Use concat instead of crossfade to prevent sync issues
            f"[a0][a1_delayed]concat=n=2:v=0:a=1[aout]"
        )
    
    def _build_three_video_filter(self, specs: Dict, trans1_start: float,
                                 trans2_start: float, duration: float) -> str:
        """Build filter for three videos with two transitions"""
        return (
            # Prepare all three videos
            f"[0:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1,format=yuva420p[v0];"
            
            f"[1:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1,format=yuva420p[v1];"
            
            f"[2:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={specs['frame_rate']},setsar=1,format=yuva420p[v2];"
            
            # Audio preparation
            f"[0:a]aresample={specs['sample_rate']}:async=1,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a0];"
            f"[1:a]aresample={specs['sample_rate']}:async=1,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a1];"
            f"[2:a]aresample={specs['sample_rate']}:async=1,"
            f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a2];"
            
            # First transition (video 0 to 1)
            f"[v0][v1]xfade=transition=fade:duration={duration}:offset={trans1_start}[v01];"
            f"[a0][a1]acrossfade=d={duration}:c1=tri:c2=tri[a01];"
            
            # Second transition (result to video 2)
            f"[v01][v2]xfade=transition=fade:duration={duration}:offset={trans2_start}[vout];"
            f"[a01][a2]acrossfade=d={duration}:c1=tri:c2=tri[aout]"
        )
    
    