# app/src/automation/orchestrator/processing/coordinator_modules/download_finder.py
"""
Download Finder Module
Locates download directories with fallback strategies
"""

import os

class DownloadFinder:
    """Finds and validates download directories"""
    
    def __init__(self):
        self.default_download_dir = "temp_downloads"
        self.alternative_paths = [
            "temp_downloads",
            "./temp_downloads",
            "../temp_downloads"
        ]
    
    def find_downloads_directory(self, config_dir=None):
        """
        Find the downloads directory using multiple strategies
        
        Args:
            config_dir: Configured download directory (optional)
            
        Returns:
            Absolute path to downloads directory or None
        """
        # Use config dir if provided
        downloads_path = config_dir or self.default_download_dir
        
        print(f"🔍 Checking downloads directory: {downloads_path}")
        
        # Convert to absolute path
        if not os.path.isabs(downloads_path):
            abs_downloads_path = os.path.abspath(downloads_path)
            print(f"   Absolute path: {abs_downloads_path}")
        else:
            abs_downloads_path = downloads_path
        
        # Check if exists
        if os.path.exists(abs_downloads_path):
            return abs_downloads_path
        
        # Try alternative locations
        print(f"⚠️ Downloads directory not found at: {abs_downloads_path}")
        
        for alt_path in self.alternative_paths:
            if os.path.exists(alt_path):
                abs_path = os.path.abspath(alt_path)
                print(f"✅ Found downloads at alternative location: {abs_path}")
                return abs_path
        
        print("❌ No temp downloads found anywhere")
        return None
    
    def list_video_files(self, directory_path):
        """
        List all video files in directory
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of video filenames
        """
        if not directory_path or not os.path.exists(directory_path):
            return []
        
        video_extensions = (
            '.mp4', '.mov', '.avi', '.mkv', 
            '.webm', '.wmv', '.flv', '.m4v'
        )
        
        try:
            all_files = os.listdir(directory_path)
            print(f"   Found {len(all_files)} total files")
            
            video_files = [
                f for f in all_files 
                if f.lower().endswith(video_extensions)
            ]
            
            print(f"   Found {len(video_files)} video files: {video_files}")
            return video_files
            
        except Exception as e:
            print(f"❌ Error listing directory: {e}")
            return []