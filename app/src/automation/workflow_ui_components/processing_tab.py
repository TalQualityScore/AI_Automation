# app/src/automation/workflow_ui_components/processing_tab.py
# COMPLETE FILE - Shows "Processing video X of Y" during batch processing

import tkinter as tk
from tkinter import ttk
import re

class ProcessingTab:
    """Handles the processing tab content and logic - WITH VIDEO COUNTER"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.progress_var = None
        self.progress_label = None
        self.step_label = None
        self.cancel_btn = None
        self.video_counter_label = None  # NEW: For showing "Processing video 2/3"
        self.total_videos = 0  # Track total number of videos
        self.current_video = 0  # Track current video being processed
        
    def create_tab(self, estimated_time: str):
        """Create processing tab content - WITH VIDEO COUNTER"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        # Processing header
        header_frame = ttk.Frame(self.frame, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(40, 30))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack()
        
        icon_label = ttk.Label(title_container, text="⚙️", font=('Segoe UI', 24),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT)
        
        ttk.Label(text_frame, text="Processing Videos", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Please wait while we process your videos...", 
                 style='Body.TLabel', font=('Segoe UI', 11),
                 foreground=self.theme.colors['text_secondary']).pack(anchor=tk.W)
        
        # Progress section
        progress_frame = ttk.Frame(self.frame, style='White.TFrame')
        progress_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           length=500)
        self.progress_bar.pack(pady=(0, 15))
        
        # Progress percentage
        self.progress_label = ttk.Label(progress_frame, text="0%",
                                       style='Body.TLabel', font=('Segoe UI', 11, 'bold'))
        self.progress_label.pack(pady=(0, 8))
        
        # NEW: Video counter label (e.g., "Processing video 2 of 3")
        self.video_counter_label = ttk.Label(progress_frame, text="",
                                            style='Body.TLabel', font=('Segoe UI', 10, 'bold'),
                                            foreground=self.theme.colors['accent'])
        self.video_counter_label.pack(pady=(0, 5))
        
        # Current step
        self.step_label = ttk.Label(progress_frame, text="Starting video processing...",
                                   style='Body.TLabel', font=('Segoe UI', 10))
        self.step_label.pack(pady=(0, 15))
        
        # Simple status message only
        ttk.Label(progress_frame, text="Processing will complete automatically",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                 foreground=self.theme.colors['text_secondary']).pack()
        
        return self.frame
    
    def update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress bar and labels - WITH VIDEO COUNTER LOGIC"""
        if self.progress_var:
            self.progress_var.set(progress)
        if self.progress_label:
            self.progress_label.config(text=f"{int(progress)}%")
        
        if step_text:
            # Check for video processing messages and extract numbers
            if any(phrase in step_text for phrase in ["Processing Version", "Processing video", "--- Processing Version"]):
                # Extract video number from messages like:
                # "--- Processing Version 01 (quiz_only) ---"
                # "--- Processing Version 02 (quiz_only) --- Video 2 of 3"
                try:
                    # Look for version numbers like 01, 02, 03
                    version_match = re.search(r'Version (\d+)', step_text)
                    if version_match:
                        self.current_video = int(version_match.group(1))
                    
                    # Look for "Video X of Y" pattern
                    video_count_match = re.search(r'Video (\d+) of (\d+)', step_text)
                    if video_count_match:
                        self.current_video = int(video_count_match.group(1))
                        self.total_videos = int(video_count_match.group(2))
                    
                    # Try to extract total from the step text or use stored value
                    if "(" in step_text and ")" in step_text:
                        # Extract total if it's in format like (1/3)
                        total_match = re.search(r'\((\d+)/(\d+)\)', step_text)
                        if total_match:
                            self.total_videos = int(total_match.group(2))
                    
                    # If we don't have total yet, try to find it from "Processing 3 files"
                    if self.total_videos == 0:
                        files_match = re.search(r'Processing (\d+) files', step_text)
                        if files_match:
                            self.total_videos = int(files_match.group(1))
                    
                    # Update the counter if we have both values
                    if self.total_videos > 0 and self.current_video > 0:
                        self.update_video_counter(self.current_video, self.total_videos)
                except Exception as e:
                    print(f"Could not extract video number: {e}")
            
            # Also check for initial file count
            elif "PROCESSED" in step_text and "FILES" in step_text:
                # Extract from "✅ PROCESSED 3 FILES"
                try:
                    files_match = re.search(r'PROCESSED (\d+) FILES', step_text)
                    if files_match:
                        self.total_videos = int(files_match.group(1))
                except:
                    pass
            
            # Check for "Processing 3 files" pattern
            elif "Processing" in step_text and "files" in step_text:
                try:
                    files_match = re.search(r'Processing (\d+) files', step_text)
                    if files_match:
                        self.total_videos = int(files_match.group(1))
                        print(f"📹 Detected total videos: {self.total_videos}")
                except:
                    pass
            
            self.step_label.config(text=step_text)
    
    def update_video_counter(self, current: int, total: int):
        """Update the video counter display"""
        if self.video_counter_label:
            self.video_counter_label.config(text=f"📹 Processing video {current} of {total}")
    
    def set_total_videos(self, total: int):
        """Set the total number of videos to process"""
        self.total_videos = total
    
    def start_processing(self):
        """Called when processing starts"""
        if self.progress_label:
            self.progress_label.config(text="0%")
        if self.step_label:
            self.step_label.config(text="Initializing processing...")
        if self.video_counter_label:
            self.video_counter_label.config(text="")
        self.total_videos = 0
        self.current_video = 0