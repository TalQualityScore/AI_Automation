# app/src/automation/workflow_ui_components/confirmation_tab/video_section.py
"""
Video Information Section
Shows video count and details
"""

import tkinter as tk
from tkinter import ttk

class VideoSection:
    """Video information section"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.create_section()
    
    def create_section(self):
        """Create video information section"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame') 
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(section_frame, text="📹 Videos to Process", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # DEBUG: Check what's in client_videos
        print("=" * 50)
        print("DEBUG: Video Section - Checking client_videos...")
        
        if hasattr(self.data, 'client_videos'):
            print(f"DEBUG: client_videos exists")
            print(f"DEBUG: client_videos type = {type(self.data.client_videos)}")
            
            if self.data.client_videos is not None:
                print(f"DEBUG: client_videos is not None")
                
                # Check if it's a list
                if isinstance(self.data.client_videos, list):
                    print(f"DEBUG: client_videos is a list with {len(self.data.client_videos)} items")
                    for i, video in enumerate(self.data.client_videos):
                        print(f"DEBUG:   Video {i+1}: {video}")
                else:
                    print(f"DEBUG: client_videos is NOT a list, it's a {type(self.data.client_videos)}")
                    print(f"DEBUG: client_videos content = {self.data.client_videos}")
            else:
                print(f"DEBUG: client_videos is None")
        else:
            print(f"DEBUG: client_videos does NOT exist in data")
            print(f"DEBUG: Available data attributes: {dir(self.data)}")
        
        # Also check for alternative names
        if hasattr(self.data, 'downloaded_videos'):
            print(f"DEBUG: Found 'downloaded_videos' instead: {self.data.downloaded_videos}")
        
        if hasattr(self.data, 'videos'):
            print(f"DEBUG: Found 'videos' instead: {self.data.videos}")
        
        print("=" * 50)
        
        # Calculate actual video count
        video_count = 0
        
        # Try different possible attribute names
        if hasattr(self.data, 'client_videos') and self.data.client_videos:
            if isinstance(self.data.client_videos, list):
                video_count = len(self.data.client_videos)
            else:
                # If it's not a list but exists, assume 1 video
                video_count = 1
        elif hasattr(self.data, 'downloaded_videos') and self.data.downloaded_videos:
            if isinstance(self.data.downloaded_videos, list):
                video_count = len(self.data.downloaded_videos)
            else:
                video_count = 1
        elif hasattr(self.data, 'videos') and self.data.videos:
            if isinstance(self.data.videos, list):
                video_count = len(self.data.videos)
            else:
                video_count = 1
        else:
            # Default to 1 if we can't find video data
            print("DEBUG: No video data found, defaulting to 1")
            video_count = 1
        
        # Create the text with proper singular/plural
        video_text = f"Found {video_count} video{'s' if video_count != 1 else ''} ready for processing"
        
        print(f"DEBUG: Final video text: {video_text}")
        
        # Display the video count
        ttk.Label(section_frame, text=video_text,
                 style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W, padx=(15, 0))