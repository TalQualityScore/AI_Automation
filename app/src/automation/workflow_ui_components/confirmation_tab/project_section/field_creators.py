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
        """Create project name field using grid for precise alignment"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # Configure grid columns for precise alignment
        info_frame.columnconfigure(0, weight=0)  # Label column - fixed width
        info_frame.columnconfigure(1, weight=1)  # Field column - expandable
        
        # Label with fixed width
        ttk.Label(info_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).grid(row=0, column=0, sticky=tk.W)
        
        self.ps.main_tab.project_name_var.set(self.ps.data.project_name)
        self.ps.main_tab.project_name_entry = ttk.Entry(
            info_frame, 
            textvariable=self.ps.main_tab.project_name_var,
            font=('Segoe UI', 10, 'bold')
        )
        # Grid with sticky=ew for right-edge alignment
        self.ps.main_tab.project_name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(5, 0))
        self.ps.main_tab.project_name_entry.bind('<KeyRelease>', 
                                                self.ps.event_handlers.on_project_name_change)
        
        print("✅ Project field created with grid layout")
    
    def create_account_dropdown(self, parent):
        """Create account dropdown using grid for precise alignment"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # Configure grid columns for precise alignment
        info_frame.columnconfigure(0, weight=0)  # Label column - fixed width
        info_frame.columnconfigure(1, weight=1)  # Field column - expandable
        
        # Label with fixed width
        ttk.Label(info_frame, text="Account:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).grid(row=0, column=0, sticky=tk.W)
        
        self.ps.main_tab.account_var.set(self.ps.dropdown_handlers.get_default_account_selection())
        account_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.ps.main_tab.account_var,
            values=self.ps.dropdown_handlers.get_account_options(),
            font=('Segoe UI', 10), 
            state='readonly'
        )
        # Grid with sticky=ew for right-edge alignment
        account_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(5, 0))
        account_combo.bind('<<ComboboxSelected>>', 
                          lambda e: self.ps.event_handlers.safe_account_change())
        
        print("✅ Account dropdown created with grid layout")
    
    def create_platform_dropdown(self, parent):
        """Create platform dropdown using grid for precise alignment"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # Configure grid columns for precise alignment
        info_frame.columnconfigure(0, weight=0)  # Label column - fixed width
        info_frame.columnconfigure(1, weight=1)  # Field column - expandable
        
        # Label with fixed width
        ttk.Label(info_frame, text="Platform:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).grid(row=0, column=0, sticky=tk.W)
        
        self.ps.main_tab.platform_var.set(self.ps.dropdown_handlers.get_default_platform_selection())
        platform_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.ps.main_tab.platform_var,
            values=self.ps.dropdown_handlers.get_platform_options(),
            font=('Segoe UI', 10), 
            state='readonly'
        )
        # Grid with sticky=ew for right-edge alignment
        platform_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(5, 0))
        platform_combo.bind('<<ComboboxSelected>>', self.ps.event_handlers.on_platform_change)
        
        print("✅ Platform dropdown created with grid layout")
    
    def create_processing_mode_multiselect(self, parent):
        """Create processing mode multiselect using grid for precise alignment"""
        # Header frame
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        # Configure grid columns for precise alignment
        info_frame.columnconfigure(0, weight=0)  # Label column - fixed width
        info_frame.columnconfigure(1, weight=1)  # Field column - expandable
        
        # Label with fixed width
        ttk.Label(info_frame, text="Processing:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).grid(row=0, column=0, sticky=tk.W)
        
        # Delegate the complex multiselect UI to mode_selector
        self.ps.mode_selector.create_multiselect_ui(info_frame)
        
        print("✅ Processing mode multiselect created with grid layout")
    
    def create_info_note(self, parent):
        """Create info note with proper left alignment to match field labels"""
        note_frame = ttk.Frame(parent, style='White.TFrame')
        note_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(note_frame, text="💡 All fields above can be edited to override auto-detection",
                 style='SpecialText.TLabel').pack(anchor=tk.W)
        
        print("✅ Info note created with left alignment")
    
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