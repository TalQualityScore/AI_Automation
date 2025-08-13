# app/src/automation/workflow_ui_components/confirmation_tab/project_section/field_creators.py
"""
Field Creators - UI Field Creation Logic
Handles creating all input fields with consistent label widths (10)
FIXED: All labels now use width=10 for proper alignment
"""

import tkinter as tk
from tkinter import ttk

class FieldCreators:
    """Handles creation of all UI fields with consistent styling"""
    
    def __init__(self, project_section):
        self.ps = project_section  # Reference to main ProjectSection
    
    def create_project_field(self, parent):
        """Create project name field - FIXED: width=10"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # FIXED: Label width=10 (was 14)
        ttk.Label(info_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
        self.ps.main_tab.project_name_var.set(self.ps.data.project_name)
        self.ps.main_tab.project_name_entry = ttk.Entry(
            info_frame, 
            textvariable=self.ps.main_tab.project_name_var,
            font=('Segoe UI', 10, 'bold'), 
            width=37
        )
        self.ps.main_tab.project_name_entry.pack(side=tk.LEFT)
        self.ps.main_tab.project_name_entry.bind('<KeyRelease>', 
                                                self.ps.event_handlers.on_project_name_change)
        
        print("✅ Project field created with width=10")
    
    def create_account_dropdown(self, parent):
        """Create account dropdown - CORRECT: width=10"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # CORRECT: Label width=10 (already correct)
        ttk.Label(info_frame, text="Account:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
        self.ps.main_tab.account_var.set(self.ps.dropdown_handlers.get_default_account_selection())
        account_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.ps.main_tab.account_var,
            values=self.ps.dropdown_handlers.get_account_options(),
            font=('Segoe UI', 10), 
            width=35, 
            state='readonly'
        )
        account_combo.pack(side=tk.LEFT)
        account_combo.bind('<<ComboboxSelected>>', 
                          lambda e: self.ps.event_handlers.safe_account_change())
        
        print("✅ Account dropdown created with width=10")
    
    def create_platform_dropdown(self, parent):
        """Create platform dropdown - CORRECT: width=10"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # CORRECT: Label width=10 (already correct)
        ttk.Label(info_frame, text="Platform:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
        self.ps.main_tab.platform_var.set(self.ps.dropdown_handlers.get_default_platform_selection())
        platform_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.ps.main_tab.platform_var,
            values=self.ps.dropdown_handlers.get_platform_options(),
            font=('Segoe UI', 10), 
            width=35, 
            state='readonly'
        )
        platform_combo.pack(side=tk.LEFT)
        platform_combo.bind('<<ComboboxSelected>>', self.ps.event_handlers.on_platform_change)
        
        print("✅ Platform dropdown created with width=10")
    
    def create_processing_mode_multiselect(self, parent):
        """Create dropdown-style multi-select processing mode section - FIXED: width=10"""
        # Header frame
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # FIXED: Label width=10 (was 14)
        ttk.Label(info_frame, text="Processing:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
        # Delegate the complex multiselect UI to mode_selector
        self.ps.mode_selector.create_multiselect_ui(info_frame)
        
        print("✅ Processing mode multiselect created with width=10")
    
    def create_info_note(self, parent):
        """Create info note"""
        note_frame = ttk.Frame(parent, style='White.TFrame')
        note_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(note_frame, text="💡 All fields above can be edited to override auto-detection",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                 foreground='#605e5c').pack()
        
        print("✅ Info note created")
    
    def get_field_label_style(self):
        """Get consistent label style for all fields"""
        return {
            'style': 'Body.TLabel',
            'font': ('Segoe UI', 10),
            'width': 10  # Consistent width for all labels
        }
    
    def get_field_entry_style(self):
        """Get consistent entry style for all fields"""
        return {
            'font': ('Segoe UI', 10),
            'width': 35
        }