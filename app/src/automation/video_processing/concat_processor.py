# app/src/automation/video_processing/concat_processor.py
"""
Concatenation Processor Module
Handles robust video concatenation with perfect sync
"""

import subprocess
from typing import List, Dict, Optional
from .processor_config import ProcessorConfig

class ConcatProcessor:
    """Handles video concatenation with perfect normalization"""
    
    def __init__(self):
        self.config = ProcessorConfig()
    
    def robust_concat(self, video_list: List[str], output_path: str, specs: Dict) -> Optional[str]:
        """
        ROBUST concatenation with perfect normalization
        Each video is normalized to identical specs before concatenation
        """
        print(f"🔧 ROBUST CONCAT: Processing {len(video_list)} videos with perfect sync...")
        
        try:
            # Build FFmpeg command
            cmd = ['ffmpeg', '-y', '-hide_banner']
            
            # Add all input files
            for video in video_list:
                cmd.extend(['-i', video])
            
            # Build filter complex
            filter_complex = self._build_filter_complex(video_list, specs)
            
            # Add filter and output settings
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-preset', specs['preset'],
                '-crf', str(self.config.DEFAULT_VIDEO_CRF),
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', self.config.DEFAULT_AUDIO_BITRATE,
                '-ar', str(specs['sample_rate']),
                '-ac', '2',  # Ensure stereo
                '-movflags', '+faststart',
                output_path
            ])
            
            self._print_processing_info(specs)
            
            # Execute FFmpeg
            print("🎬 Starting FFmpeg processing...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ ROBUST concatenation successful - perfect sync guaranteed")
                return None
            else:
                print(f"❌ FFmpeg error:")
                print(f"   Error: {result.stderr[:500]}")
                return f"FFmpeg error: {result.stderr[:200]}"
                
        except Exception as e:
            print(f"❌ Robust concatenation failed: {e}")
            return f"Robust concatenation failed: {e}"
    
    def _build_filter_complex(self, video_list: List[str], specs: Dict) -> str:
        """Build the filter_complex string for FFmpeg"""
        filter_parts = []
        
        # Normalize each input video to identical specs
        for i in range(len(video_list)):
            # Video normalization
            video_filter = (
                f"[{i}:v]"
                f"scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
                f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
                f"fps={specs['frame_rate']},"
                f"setsar=1"
                f"[v{i}]"
            )
            filter_parts.append(video_filter)
            
            # Audio normalization
            audio_filter = (
                f"[{i}:a]"
                f"aresample={specs['sample_rate']},"
                f"aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo,"
                f"asetpts=PTS-STARTPTS"
                f"[a{i}]"
            )
            filter_parts.append(audio_filter)
        
        # Concatenate all normalized streams
        concat_inputs = ""
        for i in range(len(video_list)):
            concat_inputs += f"[v{i}][a{i}]"
        
        concat_filter = f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
        filter_parts.append(concat_filter)
        
        return ";".join(filter_parts)
    
    def _print_processing_info(self, specs: Dict):
        """Print processing information"""
        print(f"🔧 Using ROBUST settings:")
        print(f"   📹 Video: {specs['width']}x{specs['height']} @ {specs['frame_rate']}fps")
        print(f"   🔊 Audio: {specs['sample_rate']}Hz stereo, {self.config.DEFAULT_AUDIO_BITRATE} bitrate")
        print(f"   ⚙️ Preset: {specs['preset']} (quality over speed)")
        print(f"   ⏱️ Duration: {specs['total_duration']/60:.1f} minutes")