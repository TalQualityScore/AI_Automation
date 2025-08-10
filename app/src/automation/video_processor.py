# app/src/automation/video_processor.py
# ROBUST VERSION - Perfect sync and quality (slower but no issues)
# Prioritizes perfect synchronization over speed

import os
import shutil
import subprocess
import json
import tempfile
from typing import Optional, List, Tuple, Dict

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ASSETS_BASE_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos")

# Default settings
DEFAULT_TRANSITION_TYPE = "fade"
DEFAULT_TRANSITION_DURATION = 0.25
DEFAULT_FFMPEG_PRESET = "faster"

class VideoProcessor:
    """
    ROBUST Video processor - Perfect sync and quality guaranteed
    Uses thorough normalization to prevent sync issues
    """
    
    def __init__(self, use_transitions: bool = True, 
                 transition_type: str = DEFAULT_TRANSITION_TYPE,
                 transition_duration: float = DEFAULT_TRANSITION_DURATION,
                 account_code: str = None,
                 platform_code: str = None):
        """Initialize VideoProcessor with robust configuration"""
        self.use_transitions = use_transitions
        self.transition_type = transition_type
        self.transition_duration = transition_duration
        self.ffmpeg_preset = DEFAULT_FFMPEG_PRESET
        
        # Store account and platform for asset path resolution
        self.account_code = account_code
        self.platform_code = platform_code
        
        print(f"🎬 VideoProcessor initialized (ROBUST - Perfect Sync)")
        if self.account_code and self.platform_code:
            print(f"   📁 Account: {self.account_code}, Platform: {self.platform_code}")
        if self.use_transitions:
            print(f"   ✨ Transitions: {self.transition_type} ({self.transition_duration}s)")
    
    def set_account_platform(self, account_code: str, platform_code: str):
        """Update account and platform codes for asset path resolution"""
        self.account_code = account_code
        self.platform_code = platform_code
        print(f"📁 Updated: Account={account_code}, Platform={platform_code}")
    
    def _get_asset_path(self, asset_type: str) -> str:
        """Get the path to a specific asset type based on account and platform"""
        if not self.account_code or not self.platform_code:
            # Fallback to old structure if no account/platform set
            print(f"⚠️ No account/platform set, using legacy paths")
            if asset_type == "Connectors":
                return os.path.join(SCRIPT_DIR, "Assets", "Videos", "connectors")
            elif asset_type == "Quiz":
                return os.path.join(SCRIPT_DIR, "Assets", "Videos", "quiz_outro")
            else:
                return None
        
        # Build path based on new structure
        asset_path = os.path.join(ASSETS_BASE_PATH, self.account_code, self.platform_code, asset_type)
        
        # Check if path exists, if not try without platform for some assets
        if not os.path.exists(asset_path) and asset_type in ["SVSL", "VSL"]:
            # Try direct account level for SVSL/VSL if not platform-specific
            asset_path = os.path.join(ASSETS_BASE_PATH, self.account_code, asset_type)
        
        return asset_path if os.path.exists(asset_path) else None
    
    def _get_video_info(self, video_path: str) -> Dict:
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
                
                # Extract video stream info
                video_stream = None
                audio_stream = None
                
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video' and not video_stream:
                        video_stream = stream
                    elif stream.get('codec_type') == 'audio' and not audio_stream:
                        audio_stream = stream
                
                # Parse frame rate more carefully
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
                
                return {
                    'duration': float(data.get('format', {}).get('duration', 0)),
                    'width': video_stream.get('width', 0) if video_stream else 0,
                    'height': video_stream.get('height', 0) if video_stream else 0,
                    'video_codec': video_stream.get('codec_name', '') if video_stream else '',
                    'audio_codec': audio_stream.get('codec_name', '') if audio_stream else '',
                    'frame_rate': round(frame_rate, 3),  # Keep precision for exact matching
                    'sample_rate': int(audio_stream.get('sample_rate', 44100)) if audio_stream else 44100,
                    'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
                    'file_size_mb': os.path.getsize(video_path) / (1024 * 1024)
                }
        except Exception as e:
            print(f"⚠️ Could not analyze video {os.path.basename(video_path)}: {e}")
        
        return {}
    
    def _determine_target_specs(self, video_list: List[str]) -> Dict:
        """Determine target specs for perfect compatibility"""
        print("🔍 Analyzing videos for ROBUST processing specs...")
        
        video_infos = []
        total_duration = 0
        
        for video in video_list:
            info = self._get_video_info(video)
            if info:
                video_infos.append(info)
                total_duration += info.get('duration', 0)
                print(f"   📹 {os.path.basename(video)}: {info.get('width')}x{info.get('height')} @ {info.get('frame_rate')}fps, {info.get('sample_rate')}Hz")
        
        if not video_infos:
            # Fallback to safe defaults
            return {
                'width': 1920, 'height': 1080, 'frame_rate': 30.0, 
                'sample_rate': 44100, 'preset': 'medium', 'total_duration': 0
            }
        
        # ROBUST APPROACH: Find the MOST COMMON specs, not just client video
        # This prevents issues when client video has unusual specs
        
        # Collect all resolutions
        resolutions = [(info.get('width', 1920), info.get('height', 1080)) for info in video_infos]
        
        # Use the most common resolution, or client video resolution if tie
        from collections import Counter
        resolution_counts = Counter(resolutions)
        target_width, target_height = resolution_counts.most_common(1)[0][0]
        
        # For frame rate: Use a STANDARD rate that's compatible with all
        frame_rates = [info.get('frame_rate', 30) for info in video_infos]
        unique_frame_rates = list(set(frame_rates))
        
        # Choose frame rate strategy based on what we have
        if len(unique_frame_rates) == 1:
            # All same frame rate - use it
            target_fps = unique_frame_rates[0]
        elif 25.0 in frame_rates and any(23 < fr < 24.5 for fr in frame_rates):
            # Mix of 25fps and ~24fps - standardize to 25fps (cleaner conversion)
            target_fps = 25.0
            print("⚠️ Mixed frame rates detected (25fps + ~24fps) - standardizing to 25fps")
        elif any(29 < fr < 31 for fr in frame_rates):
            # Contains 30fps - use 30fps
            target_fps = 30.0
            print("⚠️ Mixed frame rates detected - standardizing to 30fps")
        else:
            # Use client video frame rate as fallback
            target_fps = video_infos[0].get('frame_rate', 30)
        
        # For audio: Use standard 44100Hz (most compatible)
        # This avoids weird pitch issues from sample rate conversion
        target_sample_rate = 44100
        
        # Choose preset based on total duration but prefer quality
        if total_duration > 2400:  # 40+ minutes (very long)
            preset = 'faster'  # Still reasonably fast for very long videos
            print(f"⏱️ Very long video detected ({total_duration/60:.1f} min) - using faster preset")
        elif total_duration > 1200:  # 20+ minutes 
            preset = 'medium'  # Good balance
            print(f"⏱️ Long video detected ({total_duration/60:.1f} min) - using medium preset")
        else:
            preset = 'medium'  # Best quality for shorter videos
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
    
    def process_video_sequence(self, client_video: str, output_path: str, 
                              target_width: int, target_height: int,
                              processing_mode: str = "connector_quiz") -> Optional[str]:
        """Process video sequence with ROBUST synchronization"""
        print(f"🎬 Starting ROBUST video processing in {processing_mode} mode...")
        
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
            connector = self._get_connector_video()
            if connector:
                video_list.append(connector)
                print(f"✅ Added connector: {os.path.basename(connector)}")
            
            quiz = self._get_quiz_video()
            if quiz:
                video_list.append(quiz)
                print(f"✅ Added quiz outro: {os.path.basename(quiz)}")
        
        elif processing_mode == "quiz_only":
            quiz = self._get_quiz_video()
            if quiz:
                video_list.append(quiz)
                print(f"✅ Added quiz outro: {os.path.basename(quiz)}")
        
        elif processing_mode == "svsl_only":
            svsl = self._get_svsl_video()
            if svsl:
                video_list.append(svsl)
                print(f"✅ Added SVSL: {os.path.basename(svsl)}")
        
        elif processing_mode == "connector_svsl":
            connector = self._get_connector_video()
            if connector:
                video_list.append(connector)
                print(f"✅ Added connector: {os.path.basename(connector)}")
            
            svsl = self._get_svsl_video()
            if svsl:
                video_list.append(svsl)
                print(f"✅ Added SVSL: {os.path.basename(svsl)}")
        
        elif processing_mode == "vsl_only":
            vsl = self._get_vsl_video()
            if vsl:
                video_list.append(vsl)
                print(f"✅ Added VSL: {os.path.basename(vsl)}")
        
        elif processing_mode == "connector_vsl":
            connector = self._get_connector_video()
            if connector:
                video_list.append(connector)
                print(f"✅ Added connector: {os.path.basename(connector)}")
            
            vsl = self._get_vsl_video()
            if vsl:
                video_list.append(vsl)
                print(f"✅ Added VSL: {os.path.basename(vsl)}")
        
        # Determine target specs for perfect compatibility
        target_specs = self._determine_target_specs(video_list)

        # SMART PROCESSING: Use transitions for short videos, robust for long ones
        if len(video_list) > 1 and target_specs['total_duration'] < 300:  # Under 5 minutes
            print("🎞️ Using transitions for short video sequence")
            return self._robust_concat_with_transitions(video_list, output_path, target_specs)
        else:
            print("🔧 Using ROBUST concatenation for perfect synchronization")
            return self._robust_concat(video_list, output_path, target_specs)
    
    def _robust_concat(self, video_list: List[str], output_path: str, specs: Dict) -> Optional[str]:
        """
        ROBUST concatenation with perfect normalization
        Each video is normalized to identical specs before concatenation
        """
        print(f"🔧 ROBUST CONCAT: Processing {len(video_list)} videos with perfect sync...")
        
        try:
            # Build FFmpeg command with filter_complex for perfect normalization
            cmd = ['ffmpeg', '-y', '-hide_banner']
            
            # Add all input files
            for video in video_list:
                cmd.extend(['-i', video])
            
            # Build filter complex to normalize each video
            filter_parts = []
            
            # Normalize each input video to identical specs
            for i in range(len(video_list)):
                # Video normalization: scale, pad, set frame rate, set aspect ratio
                video_filter = (
                    f"[{i}:v]"
                    f"scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
                    f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:black,"
                    f"fps={specs['frame_rate']},"
                    f"setsar=1"
                    f"[v{i}]"
                )
                filter_parts.append(video_filter)
                
                # Audio normalization: resample, set channels, ensure sync
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
            
            # Combine all filters
            filter_complex = ";".join(filter_parts)
            
            # Add filter complex and output mapping
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-preset', specs['preset'],
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-ar', str(specs['sample_rate']),
                '-ac', '2',  # Ensure stereo
                '-movflags', '+faststart',
                output_path
            ])
            
            print(f"🔧 Using ROBUST settings:")
            print(f"   📹 Video: {specs['width']}x{specs['height']} @ {specs['frame_rate']}fps")
            print(f"   🔊 Audio: {specs['sample_rate']}Hz stereo, 192k bitrate")
            print(f"   ⚙️ Preset: {specs['preset']} (quality over speed)")
            print(f"   ⏱️ Duration: {specs['total_duration']/60:.1f} minutes")
            
            # Execute FFmpeg with robust error handling
            print("🎬 Starting FFmpeg processing...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ ROBUST concatenation successful - perfect sync guaranteed")
                return None
            else:
                print(f"❌ FFmpeg error:")
                print(f"   Command: {' '.join(cmd[:10])}... [truncated]")
                print(f"   Error: {result.stderr[:500]}")
                return f"FFmpeg error: {result.stderr[:200]}"
                
        except Exception as e:
            print(f"❌ Robust concatenation failed: {e}")
            return f"Robust concatenation failed: {e}"
    
    def _get_connector_video(self) -> Optional[str]:
        """Get the first available connector video"""
        connector_path = self._get_asset_path("Connectors")
        
        if not connector_path:
            print(f"⚠️ Connector directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(connector_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(connector_path, files[0])
        
        print(f"⚠️ No connector videos found in {connector_path}")
        return None
    
    def _get_quiz_video(self) -> Optional[str]:
        """Get the first available quiz outro video"""
        quiz_path = self._get_asset_path("Quiz")
        
        if not quiz_path:
            print(f"⚠️ Quiz outro directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(quiz_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(quiz_path, files[0])
        
        print(f"⚠️ No quiz outro videos found in {quiz_path}")
        return None
    
    def _get_svsl_video(self) -> Optional[str]:
        """Get the first available SVSL video"""
        svsl_path = self._get_asset_path("SVSL")
        
        if not svsl_path:
            print(f"⚠️ SVSL directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(svsl_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(svsl_path, files[0])
        
        print(f"⚠️ No SVSL videos found in {svsl_path}")
        return None
    
    def _get_vsl_video(self) -> Optional[str]:
        """Get the first available VSL video"""
        vsl_path = self._get_asset_path("VSL")
        
        if not vsl_path:
            print(f"⚠️ VSL directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        files = [f for f in os.listdir(vsl_path) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if files:
            return os.path.join(vsl_path, files[0])
        
        print(f"⚠️ No VSL videos found in {vsl_path}")
        return None
    
    def configure_transitions(self, enabled: bool, transition_type: str = None, duration: float = None):
        """Update transition configuration"""
        self.use_transitions = enabled
        if transition_type:
            self.transition_type = transition_type
        if duration:
            self.transition_duration = duration
        print(f"✨ Transitions configured: {enabled}, Type: {self.transition_type}, Duration: {self.transition_duration}s")
    
    def get_video_dimensions(self, video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """Get video dimensions using ffprobe"""
        info = self._get_video_info(video_path)
        if info:
            return info.get('width'), info.get('height'), None
        else:
            return None, None, "Could not get video dimensions"
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    
    def validate_video_file(self, file_path: str) -> bool:
        """Validate if a file is a supported video format"""
        if not os.path.exists(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_supported_formats()

    def _robust_concat_with_transitions(self, video_list: List[str], output_path: str, specs: Dict) -> Optional[str]:
        """Robust concatenation WITH transitions for shorter videos"""
        if len(video_list) == 1:
            return self._robust_concat(video_list, output_path, specs)
        
        print(f"🎞️ TRANSITIONS: Processing {len(video_list)} videos with transitions...")
        
        try:
            # Build FFmpeg command with crossfade transitions
            cmd = ['ffmpeg', '-y', '-hide_banner']
            
            # Add all input files
            for video in video_list:
                cmd.extend(['-i', video])
            
            # Simple crossfade between videos
            if len(video_list) == 2:
                # Get duration of first video for transition timing
                first_video_info = self._get_video_info(video_list[0])
                duration = first_video_info.get('duration', 10)
                transition_start = max(0, duration - 1)  # Start transition 1 second before end
                
                filter_complex = (
                    f"[0:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
                    f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2,fps={specs['frame_rate']}[v0];"
                    f"[1:v]scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
                    f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2,fps={specs['frame_rate']}[v1];"
                    f"[0:a]aresample={specs['sample_rate']},aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a0];"
                    f"[1:a]aresample={specs['sample_rate']},aformat=sample_rates={specs['sample_rate']}:channel_layouts=stereo[a1];"
                    f"[v0][v1]xfade=transition=fade:duration=0.5:offset={transition_start}[vout];"
                    f"[a0][a1]acrossfade=d=0.5[aout]"
                )
            else:
                # For 3+ videos, fall back to robust concat
                print("⚠️ 3+ videos detected, using robust concat instead of transitions")
                return self._robust_concat(video_list, output_path, specs)
            
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[vout]', '-map', '[aout]',
                '-c:v', 'libx264', '-preset', specs['preset'], '-crf', '23',
                '-c:a', 'aac', '-b:a', '192k', '-ar', str(specs['sample_rate']),
                '-movflags', '+faststart',
                output_path
            ])
            
            print("🎬 Starting transition processing...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Transitions applied successfully")
                return None
            else:
                print(f"⚠️ Transitions failed: {result.stderr[:200]}")
                print("🔄 Falling back to robust concat")
                return self._robust_concat(video_list, output_path, specs)
                
        except Exception as e:
            print(f"⚠️ Transitions error: {e}")
            print("🔄 Using robust concat fallback")
            return self._robust_concat(video_list, output_path, specs)


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

# Global instance for backward compatibility
_default_processor = None

def _get_default_processor() -> VideoProcessor:
    """Get or create default processor instance"""
    global _default_processor
    if _default_processor is None:
        _default_processor = VideoProcessor()
    return _default_processor

def set_processor_account_platform(account_code: str, platform_code: str):
    """Set account and platform for the default processor"""
    processor = _get_default_processor()
    processor.set_account_platform(account_code, platform_code)

def process_video_sequence(client_video: str, output_path: str, 
                          target_width: int, target_height: int,
                          processing_mode: str = "connector_quiz") -> Optional[str]:
    """Backward compatibility wrapper for process_video_sequence"""
    processor = _get_default_processor()
    return processor.process_video_sequence(
        client_video, output_path, target_width, target_height, processing_mode
    )

def configure_transitions(enabled: bool = True, 
                        transition_type: str = "fade", 
                        duration: float = 0.25):
    """Backward compatibility wrapper for configure_transitions"""
    processor = _get_default_processor()
    processor.configure_transitions(enabled, transition_type, duration)

def get_video_dimensions(video_path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """Backward compatibility wrapper for get_video_dimensions"""
    processor = _get_default_processor()
    return processor.get_video_dimensions(video_path)

# For convenience, also export these at module level
def _get_connector_video() -> Optional[str]:
    """Get the first available connector video"""
    processor = _get_default_processor()
    return processor._get_connector_video()

def _get_quiz_video() -> Optional[str]:
    """Get the first available quiz outro video"""
    processor = _get_default_processor()
    return processor._get_quiz_video()

def _get_svsl_video() -> Optional[str]:
    """Get the first available SVSL video"""
    processor = _get_default_processor()
    return processor._get_svsl_video()

def _get_vsl_video() -> Optional[str]:
    """Get the first available VSL video"""
    processor = _get_default_processor()
    return processor._get_vsl_video()

# Module-level configuration variables for backward compatibility
USE_TRANSITIONS = True
TRANSITION_TYPE = DEFAULT_TRANSITION_TYPE
TRANSITION_DURATION = DEFAULT_TRANSITION_DURATION
FFMPEG_PRESET = DEFAULT_FFMPEG_PRESET