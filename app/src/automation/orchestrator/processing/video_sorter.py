# app/src/automation/orchestrator/processing/video_sorter.py
"""
Video Sorter Module - Handles video sorting and version letter extraction
"""

import os
import re

class VideoSorter:
    """Handles video sorting and version identification"""
    
    def extract_version_letter(self, filename):
        """Extract version letter (A, B, C, etc.) from filename
        
        Args:
            filename: Video filename to extract letter from
            
        Returns:
            Version letter (A, B, C, etc.) or None if not found
        """
        patterns = [
            r'_([A-Z])\.mp4$',
            r'-([A-Z])\.mp4$',
            r'([A-Z])\.mp4$',
            r'_([A-Z])_\d+\.mp4$',
            r'-([A-Z])_\d+\.mp4$',
            r'_\d{6}([A-Z])\.mp4$',  # Pattern for _250721C.mp4
            r'_\d{8}([A-Z])\.mp4$',  # Pattern for _20240408A.mp4
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def sort_videos_by_version_letter(self, videos):
        """Sort videos alphabetically by version letter (A → B → C)
        
        Args:
            videos: List of video file paths to sort
            
        Returns:
            Sorted list of video paths
        """
        videos_with_letters = []
        videos_without_letters = []
        
        for video in videos:
            filename = os.path.basename(video)
            letter = self.extract_version_letter(filename)
            if letter:
                videos_with_letters.append((video, letter))
            else:
                videos_without_letters.append(video)
        
        # Sort by letter
        videos_with_letters.sort(key=lambda x: x[1])
        
        # Combine: lettered videos first, then non-lettered
        sorted_videos = [v[0] for v in videos_with_letters] + videos_without_letters
        
        # Print sorting results
        print("\n📄 Video sorting results:")
        for i, video in enumerate(sorted_videos, 1):
            filename = os.path.basename(video)
            letter = self.extract_version_letter(filename)
            if letter:
                print(f"   {i}. {filename} (Version {letter} → v{i:02d})")
            else:
                print(f"   {i}. {filename} (No version → v{i:02d})")
        
        return sorted_videos