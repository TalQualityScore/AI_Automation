# app/src/automation/reports/report_modules/duration_calculator.py
"""
Duration Calculator Module
Handles video duration calculations using ffprobe
"""

import os
import subprocess
import json

class DurationCalculator:
    """Calculates and caches video durations"""
    
    def __init__(self):
        self.duration_cache = {}
    
    def get_video_duration(self, video_path):
        """
        Get actual duration of a video file using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds (float)
        """
        # Check cache first
        if video_path in self.duration_cache:
            return self.duration_cache[video_path]
        
        try:
            # Try format duration first
            duration = self._get_format_duration(video_path)
            
            if duration == 0:
                # Fallback to stream duration
                duration = self._get_stream_duration(video_path)
            
            # Cache the result
            self.duration_cache[video_path] = duration
            
            if duration > 0:
                print(f"📹 Got duration for {os.path.basename(video_path)}: {duration:.2f} seconds")
            else:
                print(f"⚠️ Could not get duration for {os.path.basename(video_path)}")
            
            return duration
            
        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout getting duration for {os.path.basename(video_path)}")
            return 0
        except Exception as e:
            print(f"⚠️ Error getting duration for {os.path.basename(video_path)}: {e}")
            return 0
    
    def _get_format_duration(self, video_path):
        """Get duration from format information"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'format' in data and 'duration' in data['format']:
                return float(data['format']['duration'])
        
        return 0
    
    def _get_stream_duration(self, video_path):
        """Get duration from stream information"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=duration',
            '-of', 'json', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'streams' in data and len(data['streams']) > 0:
                if 'duration' in data['streams'][0]:
                    return float(data['streams'][0]['duration'])
        
        return 0
    
    def format_duration(self, seconds):
        """Convert seconds to MM:SS format"""
        if seconds == 0:
            return "00:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def format_timecode(self, start_seconds, end_seconds):
        """Format a time range as MM:SS - MM:SS"""
        return f"{self.format_duration(start_seconds)} - {self.format_duration(end_seconds)}"