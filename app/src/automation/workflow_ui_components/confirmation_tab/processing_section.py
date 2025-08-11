# app/src/automation/workflow_ui_components/confirmation_tab/processing_section.py
"""
Processing Options Section
Handles transition settings and other processing options
"""

import tkinter as tk
from tkinter import ttk

class ProcessingSection:
    """Processing options section"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.create_section()
    
    def create_section(self):
        """Create processing options section"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(section_frame, text="⚙️ Processing Options", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # Transition checkbox with callback to refresh summary
        transition_frame = ttk.Frame(section_frame, style='White.TFrame')
        transition_frame.pack(fill=tk.X, padx=(15, 0), pady=2)
        
        transition_checkbox = ttk.Checkbutton(
            transition_frame, 
            text="Apply video transitions",
            variable=self.main_tab.use_transitions, 
            style='Body.TCheckbutton',
            command=self._on_transition_change
        )
        transition_checkbox.pack(anchor=tk.W)
    
    def _on_transition_change(self):
        """Handle transition setting change"""
        print(f"🔄 Transitions: {'ENABLED' if self.main_tab.use_transitions.get() else 'DISABLED'}")
        self.main_tab.refresh_summary()