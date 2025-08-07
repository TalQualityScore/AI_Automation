# app/src/automation/transitions/video_info.py
"""
Handles video information extraction using ffprobe
"""

import subprocess
import json

class VideoInfo:
    """Extract and manage video information"""
    
    @staticmethod
    def get_info(video_path):
        """
        Get comprehensive video information
        
        Returns:
            dict: Video info including width, height, duration
            None: If error occurs
        """
        command = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'stream=width,height,duration,codec_name,r_frame_rate:format=duration',
            '-of', 'json', video_path
        ]
        
        try:
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            data = json.loads(result.stdout)
            
            info = {}
            
            # Extract stream info
            if 'streams' in data:
                for stream in data['streams']:
                    if 'width' in stream and 'height' in stream:
                        info['width'] = stream['width']
                        info['height'] = stream['height']
                    if 'duration' in stream:
                        info['duration'] = float(stream['duration'])
            
            # Fallback to format duration
            if 'duration' not in info and 'format' in data:
                if 'duration' in data['format']:
                    info['duration'] = float(data['format']['duration'])
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting video info: {e}")
            return None
    
    @staticmethod
    def get_duration(video_path):
        """Get just the duration of a video"""
        info = VideoInfo.get_info(video_path)
        return info.get('duration', 0) if info else 0
    
    @staticmethod
    def get_dimensions(video_path):
        """Get video dimensions"""
        info = VideoInfo.get_info(video_path)
        if info and 'width' in info and 'height' in info:
            return info['width'], info['height']
        return None, None