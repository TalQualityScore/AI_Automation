# app/src/automation/video_processing/video_analyzer.py
"""
Video Analyzer Module
Analyzes video files and extracts information
"""

import os
import subprocess
import json
from typing import Dict, List, Tuple, Optional
from collections import Counter
from .processor_config import ProcessorConfig

_fallback_dimensions = None

def set_fallback_dimensions(width, height):
    """Set fallback dimensions for video processing when FFmpeg fails"""
    global _fallback_dimensions
    _fallback_dimensions = (width, height)
    print(f"🔧 Fallback dimensions set: {width}x{height}")

def get_fallback_dimensions():
    """Get fallback dimensions"""
    global _fallback_dimensions
    return _fallback_dimensions or (1080, 1920)  # Default 9:16 vertical

def get_video_dimensions_with_fallback(video_path):
    """Get video dimensions with fallback support"""
    try:
        # Try normal FFmpeg method first (your existing get_video_dimensions)
        analyzer = VideoAnalyzer()  # or use existing instance
        return analyzer.get_video_dimensions(video_path)
    except Exception as e:
        print(f"⚠️ FFmpeg failed for {video_path}: {e}")
        print(f"🔧 Using fallback dimensions: {get_fallback_dimensions()}")
        return get_fallback_dimensions()

class VideoAnalyzer:
    """Analyzes video files for specifications and compatibility"""
    
    def __init__(self):
        self.config = ProcessorConfig()
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get detailed video information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Extract stream info
                video_stream = None
                audio_stream = None
                
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video' and not video_stream:
                        video_stream = stream
                    elif stream.get('codec_type') == 'audio' and not audio_stream:
                        audio_stream = stream
                
                # Parse frame rate
                frame_rate = self._parse_frame_rate(video_stream)
                
                return {
                    'duration': float(data.get('format', {}).get('duration', 0)),
                    'width': video_stream.get('width', 0) if video_stream else 0,
                    'height': video_stream.get('height', 0) if video_stream else 0,
                    'video_codec': video_stream.get('codec_name', '') if video_stream else '',
                    'audio_codec': audio_stream.get('codec_name', '') if audio_stream else '',
                    'frame_rate': round(frame_rate, 3),
                    'sample_rate': int(audio_stream.get('sample_rate', 44100)) if audio_stream else 44100,
                    'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
                    'file_size_mb': os.path.getsize(video_path) / (1024 * 1024)
                }
        except Exception as e:
            print(f"⚠️ Could not analyze video {os.path.basename(video_path)}: {e}")
        
        return {}
    
    def _parse_frame_rate(self, video_stream) -> float:
        """Parse frame rate from video stream"""
        frame_rate = 30  # default
        
        if video_stream and video_stream.get('r_frame_rate'):
            try:
                r_frame_rate = video_stream['r_frame_rate']
                if '/' in r_frame_rate:
                    num, den = map(int, r_frame_rate.split('/'))
                    frame_rate = num / den if den != 0 else 30
                else:
                    frame_rate = float(r_frame_rate)
            except:
                frame_rate = 30
        
        return frame_rate
    
    def get_video_dimensions(self, video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """Get video dimensions"""
        info = self.get_video_info(video_path)
        if info:
            return info.get('width'), info.get('height'), None
        else:
            return None, None, "Could not get video dimensions"
    
    def determine_target_specs(self, video_list: List[str]) -> Dict:
        """Determine target specs for perfect compatibility"""
        print("🔍 Analyzing videos for ROBUST processing specs...")
        
        video_infos = []
        total_duration = 0
        
        for video in video_list:
            info = self.get_video_info(video)
            if info:
                video_infos.append(info)
                total_duration += info.get('duration', 0)
                print(f"   📹 {os.path.basename(video)}: {info.get('width')}x{info.get('height')} @ {info.get('frame_rate')}fps, {info.get('sample_rate')}Hz")
        
        if not video_infos:
            # Fallback to safe defaults
            return {
                'width': self.config.DEFAULT_WIDTH,
                'height': self.config.DEFAULT_HEIGHT,
                'frame_rate': self.config.DEFAULT_FRAME_RATE,
                'sample_rate': self.config.DEFAULT_SAMPLE_RATE,
                'preset': 'medium',
                'total_duration': 0
            }
        
        # Find most common resolution
        resolutions = [(info.get('width', 1920), info.get('height', 1080)) for info in video_infos]
        resolution_counts = Counter(resolutions)
        target_width, target_height = resolution_counts.most_common(1)[0][0]
        
        # Determine target frame rate
        target_fps = self._determine_target_fps(video_infos)
        
        # Standard audio rate for compatibility
        target_sample_rate = self.config.DEFAULT_SAMPLE_RATE
        
        # Choose preset based on duration
        preset = self.config.get_preset_for_duration(total_duration)
        
        if total_duration > self.config.VERY_LONG_VIDEO_THRESHOLD:
            print(f"⏱️ Very long video detected ({total_duration/60:.1f} min) - using faster preset")
        elif total_duration > self.config.LONG_VIDEO_THRESHOLD:
            print(f"⏱️ Long video detected ({total_duration/60:.1f} min) - using medium preset")
        else:
            print(f"⏱️ Standard video detected ({total_duration/60:.1f} min) - using medium preset")
        
        specs = {
            'width': target_width,
            'height': target_height,
            'frame_rate': target_fps,
            'sample_rate': target_sample_rate,
            'preset': preset,
            'total_duration': total_duration
        }
        
        print(f"🎯 ROBUST target specs: {target_width}x{target_height} @ {target_fps}fps, {target_sample_rate}Hz, preset={preset}")
        
        return specs
    
    def _determine_target_fps(self, video_infos: List[Dict]) -> float:
        """Determine the best target frame rate"""
        frame_rates = [info.get('frame_rate', 30) for info in video_infos]
        unique_frame_rates = list(set(frame_rates))
        
        if len(unique_frame_rates) == 1:
            return unique_frame_rates[0]
        elif 25.0 in frame_rates and any(23 < fr < 24.5 for fr in frame_rates):
            print("⚠️ Mixed frame rates detected (25fps + ~24fps) - standardizing to 25fps")
            return 25.0
        elif any(29 < fr < 31 for fr in frame_rates):
            print("⚠️ Mixed frame rates detected - standardizing to 30fps")
            return 30.0
        else:
            return video_infos[0].get('frame_rate', 30)
    
    def validate_video_file(self, file_path: str) -> bool:
        """Validate if a file is a supported video format"""
        if not os.path.exists(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.config.SUPPORTED_VIDEO_FORMATS
    
    def get_video_dimensions_with_fallback(self, video_path):
        """Get video dimensions with fallback support"""
        try:
            return self.get_video_dimensions(video_path)
        except Exception as e:
            print(f"⚠️ FFmpeg failed for {video_path}: {e}")
            print(f"🔧 Using fallback dimensions: {get_fallback_dimensions()}")
            fallback_width, fallback_height = get_fallback_dimensions()
            return (fallback_width, fallback_height, None)

        # Export the fallback functions
        __all__ = getattr(__all__, []) + [
            'set_fallback_dimensions',
            'get_fallback_dimensions', 
            'get_video_dimensions_with_fallback'
        ]
    
    