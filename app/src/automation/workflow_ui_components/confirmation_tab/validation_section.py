# app/src/automation/workflow_ui_components/confirmation_tab/validation_section.py
"""
Validation Issues Section
Shows validation issues if any exist
"""

import tkinter as tk
from tkinter import ttk

class ValidationSection:
    """Validation issues section"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.create_section()
    
    def create_section(self):
        """Create validation section if issues exist"""
        # Only create section if there are validation issues
        if not hasattr(self.data, 'issues') or not self.data.issues:
            return
        
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(section_frame, text="⚠️ Validation Issues", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold'), foreground='#d83b01').pack(anchor=tk.W)
        
        for issue in self.data.issues:
            issue_frame = ttk.Frame(section_frame, style='White.TFrame')
            issue_frame.pack(fill=tk.X, pady=1)
            
            ttk.Label(issue_frame, text=f"• {issue.message}", style='Body.TLabel',
                     font=('Segoe UI', 9), foreground='#d83b01').pack(anchor=tk.W, padx=(15, 0))