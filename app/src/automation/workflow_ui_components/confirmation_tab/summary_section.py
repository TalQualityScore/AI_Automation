# app/src/automation/workflow_ui_components/confirmation_tab/summary_section.py
"""
Processing Summary Section
Dynamic summary that updates when settings change
"""

import tkinter as tk
from tkinter import ttk

class SummarySection:
    """Processing summary section"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.section_frame = None
        self.create_section()
    
    def create_section(self):
        """Create processing summary section"""
        self.section_frame = ttk.Frame(self.parent, style='White.TFrame')
        self.section_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.section_frame, text="📋 Processing Summary", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        self.summary_frame = ttk.Frame(self.section_frame, style='White.TFrame')
        self.summary_frame.pack(fill=tk.X, padx=(15, 0), pady=2)
        
        self._update_summary_content()
    
    def _update_summary_content(self):
        """Update summary content based on current settings"""
        # Clear existing content
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # DEBUG: Let's see what's actually in the data
        print("=" * 50)
        print("DEBUG: Summary Section - Inspecting data")
        print(f"DEBUG: data type = {type(self.data)}")
        print(f"DEBUG: data attributes = {dir(self.data)}")
        
        if hasattr(self.data, 'client_videos'):
            print(f"DEBUG: client_videos type = {type(self.data.client_videos)}")
            if isinstance(self.data.client_videos, list):
                print(f"DEBUG: client_videos length = {len(self.data.client_videos)}")
                for i, video in enumerate(self.data.client_videos):
                    print(f"DEBUG:   Video {i+1}: {video}")
            else:
                print(f"DEBUG: client_videos value = {self.data.client_videos}")
        
        if hasattr(self.data, 'file_sizes'):
            print(f"DEBUG: file_sizes = {self.data.file_sizes}")
        print("=" * 50)
        
        # Get REAL video count from the actual data
        video_count = 0
        
        if hasattr(self.data, 'client_videos') and self.data.client_videos:
            if isinstance(self.data.client_videos, list):
                # Count only non-empty entries
                actual_videos = [v for v in self.data.client_videos if v]
                video_count = len(actual_videos)
            else:
                video_count = 1
        
        # If we still have 0, default to 1
        if video_count == 0:
            video_count = 1
        
        ttk.Label(self.summary_frame, 
                text=f"• {video_count} client video{'s' if video_count != 1 else ''} will be processed",
                style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Current processing mode
        current_mode = self.main_tab.processing_mode_var.get() if hasattr(self.main_tab, 'processing_mode_var') else getattr(self.data, 'processing_mode', 'Add Quiz Outro')
        
        # Determine endpoint
        if 'Quiz' in current_mode:
            endpoint = "Quiz Outro"
        elif 'SVSL' in current_mode:
            endpoint = "SVSL"
        elif 'VSL' in current_mode:
            endpoint = "VSL"
        elif 'Save' in current_mode:
            endpoint = "No processing (Save As Is)"
        else:
            endpoint = "Quiz Outro"
        
        # Videos will be connected to
        ttk.Label(self.summary_frame, 
                text=f"• Videos will be connected to: {endpoint}",
                style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Transition setting
        if self.main_tab.use_transitions.get():
            ttk.Label(self.summary_frame, 
                    text="• Processing type: with smooth transitions",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        else:
            ttk.Label(self.summary_frame, 
                    text="• Processing type: without transitions",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Estimated time
        ttk.Label(self.summary_frame, 
                text=f"• Estimated processing time: {self.data.estimated_time}",
                style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)

    def refresh(self):
        """Refresh summary when settings change"""
        self._update_summary_content()