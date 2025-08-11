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
        
        # FIXED: Use actual video count and correct singular/plural
        video_count = len(self.data.client_videos) if hasattr(self.data, 'client_videos') and self.data.client_videos else 0
        video_text = f"Found {video_count} video{'s' if video_count != 1 else ''} ready for processing"
        
        ttk.Label(section_frame, text=video_text,
                 style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W, padx=(15, 0))  # FIXED: 2 points smaller font
        
        # REMOVED: Total size display - not needed since it will be in breakdown at the end