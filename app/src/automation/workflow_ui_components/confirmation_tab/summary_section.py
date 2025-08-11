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
        
        # FIXED: Use actual video count from data
        video_count = len(self.data.client_videos) if hasattr(self.data, 'client_videos') and self.data.client_videos else 0
        ttk.Label(self.summary_frame, text=f"• {video_count} client video{'s' if video_count != 1 else ''} will be processed",
                 style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)  # FIXED: 2 points smaller font
        
        # FIXED: Processing type with connector format
        current_mode = self.main_tab.processing_mode_var.get() if hasattr(self.main_tab, 'processing_mode_var') else getattr(self.data, 'processing_mode', 'Add Quiz Outro')
        
        # Determine endpoint and connector
        has_connector = 'Connector' in current_mode
        
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
        
        # FIXED: Combine connector + endpoint in one line
        if has_connector and endpoint != "No processing (Save As Is)":
            connection_text = f"Connector + {endpoint}"
        else:
            connection_text = endpoint
        
        ttk.Label(self.summary_frame, text=f"• Videos will be connected to: {connection_text}",
                 style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)  # FIXED: 2 points smaller font
        
        # Transition type
        transition_text = "with smooth transitions" if self.main_tab.use_transitions.get() else "with simple stitching"
        ttk.Label(self.summary_frame, text=f"• Processing type: {transition_text}",
                 style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)  # FIXED: 2 points smaller font
        
        # Estimated time (if available)
        if hasattr(self.data, 'estimated_time') and self.data.estimated_time:
            ttk.Label(self.summary_frame, text=f"• Estimated processing time: {self.data.estimated_time}",
                     style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)  # FIXED: 2 points smaller font
    
    def refresh(self):
        """Refresh summary when settings change"""
        self._update_summary_content()