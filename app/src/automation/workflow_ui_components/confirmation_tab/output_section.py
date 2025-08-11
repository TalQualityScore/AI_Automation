# app/src/automation/workflow_ui_components/confirmation_tab/output_section.py
"""
Output Location Section
Shows where the processed videos will be saved
"""

import tkinter as tk
from tkinter import ttk

class OutputSection:
    """Output location section"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.output_location_label = None
        self.create_section()
    
    def create_section(self):
        """Create output location section"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(section_frame, text="📁 Output Location", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        location_text = getattr(self.data, 'output_location', 'Will be determined during processing')
        self.output_location_label = ttk.Label(
            section_frame, 
            text=location_text,
            style='Body.TLabel', 
            font=('Segoe UI', 9),
            foreground='#605e5c'
        )
        self.output_location_label.pack(anchor=tk.W, padx=(15, 0))
    
    def refresh(self):
        """Refresh output location display"""
        if self.output_location_label:
            location_text = getattr(self.data, 'output_location', 'Will be determined during processing')
            self.output_location_label.config(text=location_text)