# app/src/automation/workflow_ui_components/confirmation_tab.py - COMPLETE WITH FIXES

import tkinter as tk
from tkinter import ttk
from typing import Optional
from ..workflow_data_models import ConfirmationData, ValidationIssue  # ADDED: All required imports

class ConfirmationTab:
    """Confirmation tab for workflow dialog with compact layout"""
    
    def __init__(self, parent: ttk.Frame, data, theme):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.orchestrator = None
        self.dialog_controller = None
        
        # State variables
        self.use_transitions = tk.BooleanVar(value=True)
        
        self._create_ui()
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference"""
        self.orchestrator = orchestrator
        print(f"✅ ConfirmationTab: Orchestrator reference set")
    
    def set_dialog_controller(self, controller):
        """Set dialog controller reference"""
        self.dialog_controller = controller
        print(f"✅ ConfirmationTab: Dialog controller reference set")
    
    def get_updated_data(self):
        """Get the current confirmation data (for project name updates)"""
        # Update the data with the current project name from the entry field
        if hasattr(self, 'project_name_var'):
            self.data.project_name = self.project_name_var.get()
        return self.data
    
    def _on_project_name_change(self, event=None):
        """Handle project name changes"""
        new_name = self.project_name_var.get()
        if new_name != self.data.project_name:
            print(f"📝 Project name changed: '{self.data.project_name}' → '{new_name}'")
            old_name = self.data.project_name
            self.data.project_name = new_name
            
            # Update output location to reflect new project name
            if hasattr(self.data, 'output_location'):
                # Replace old project name with new one in output location
                self.data.output_location = self.data.output_location.replace(old_name, new_name)
                # Refresh the output location display
                self._refresh_output_location()
    
    def get_transition_setting(self):
        """Get the current transition setting"""
        return self.use_transitions.get()
    
    def create_tab(self):
        """Create and return the tab frame - REQUIRED by TabManager"""
        if not hasattr(self, 'frame'):
            self.frame = ttk.Frame(self.parent, style='White.TFrame')
            # Build the UI in this frame
            self._create_ui_in_frame(self.frame)
        return self.frame
    
    def _create_ui(self):
        """DEPRECATED - Use create_tab() instead"""
        # This method exists for backward compatibility
        # The actual UI is created in _create_ui_in_frame
        pass
    
    def _create_ui_in_frame(self, parent_frame):
        """Create confirmation UI with compact spacing in the given frame"""
        # Create scrollable container with reduced padding
        canvas = tk.Canvas(parent_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='White.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main content with MORE compact vertical padding
        content_frame = ttk.Frame(scrollable_frame, style='White.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=(10, 10))  # REDUCED from (15, 15)
        
        # Title with MORE compact spacing
        title_frame = ttk.Frame(content_frame, style='White.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 10))  # REDUCED from (0, 15)
        
        ttk.Label(title_frame, text="📋", font=('Segoe UI', 20),  # Was 24
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        text_frame = ttk.Frame(title_frame, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="Review & Confirm", style='Header.TLabel',
                 font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W)  # Was 18
        ttk.Label(text_frame, text="Please review the information below before processing",
                 style='Subheader.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W)  # Was 11
        
        # Sections with compact spacing
        self._add_project_info(content_frame)
        self._add_processing_options(content_frame)  # MOVED: Now BEFORE "Will Process"
        self._add_processing_details(content_frame)
        self._add_output_location(content_frame)
        
        # REMOVED DUPLICATE BUTTONS - TabManager handles button creation
        # The buttons were here (lines 86-120 in original) but are now removed
        # since TabManager._add_confirmation_buttons() creates them
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _add_project_info(self, parent):
        """Add project information section with MORE compact spacing"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))  # REDUCED from (0, 15)
        
        # Project - WITH EDITABLE FIELD
        info_frame = ttk.Frame(section_frame, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)  # REDUCED from 3
        ttk.Label(info_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=12).pack(side=tk.LEFT)  # Was 11
        
        # EDITABLE project name entry
        self.project_name_var = tk.StringVar(value=self.data.project_name)
        self.project_name_entry = ttk.Entry(info_frame, textvariable=self.project_name_var,
                                           font=('Segoe UI', 10, 'bold'), width=40)
        self.project_name_entry.pack(side=tk.LEFT)
        self.project_name_entry.bind('<KeyRelease>', self._on_project_name_change)
        
        # Account
        info_frame = ttk.Frame(section_frame, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)  # REDUCED from 3
        ttk.Label(info_frame, text="Account:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=12).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=self.data.account, style='Body.TLabel',  # FIXED: Changed from account_info to account
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Platform
        info_frame = ttk.Frame(section_frame, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)  # REDUCED from 3
        ttk.Label(info_frame, text="Platform:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=12).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=self.data.platform, style='Body.TLabel',
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Mode
        info_frame = ttk.Frame(section_frame, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)  # REDUCED from 3
        ttk.Label(info_frame, text="Mode:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=12).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=self.data.processing_mode, style='Body.TLabel',  # FIXED: Changed from mode to processing_mode
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
    
    def _add_processing_options(self, parent):
        """Add processing options section BEFORE Will Process section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))  # REDUCED from (0, 15)
        
        ttk.Label(section_frame, text="Processing Options:", style='Body.TLabel',
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 4))  # REDUCED from (0, 6)
        
        # Transition checkbox container - ALIGNED LEFT
        transition_frame = ttk.Frame(section_frame, style='White.TFrame')
        transition_frame.pack(fill=tk.X, pady=2)  # REMOVED padx to align left, REDUCED pady from 3
        
        # Checkbox for transitions - SIMPLIFIED TEXT
        transition_cb = ttk.Checkbutton(
            transition_frame,
            text="Add smooth transitions between videos",
            variable=self.use_transitions,
            command=self._update_processing_list
        )
        transition_cb.pack(anchor=tk.W)
        
        # Warning text on new line with reduced font - SIMPLIFIED TEXT
        warning_label = ttk.Label(
            section_frame, 
            text="May increase processing time by ~30%",
            style='Body.TLabel',
            font=('Segoe UI', 8, 'italic'),  # Was 9
            foreground='#888888'
        )
        warning_label.pack(anchor=tk.W, padx=(20, 0), pady=(0, 2))  # REDUCED from padx=(40, 0) and pady=(0, 3)
    
    def _add_processing_details(self, parent):
        """Add processing details section"""
        self.details_frame = ttk.Frame(parent, style='White.TFrame')
        self.details_frame.pack(fill=tk.X, pady=(0, 10))  # REDUCED from (0, 15)
        
        ttk.Label(self.details_frame, text="Will Process:", style='Body.TLabel',
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 4))  # REDUCED from (0, 6)
        
        # Create container for dynamic processing list
        self.processing_list_frame = ttk.Frame(self.details_frame, style='White.TFrame')
        self.processing_list_frame.pack(fill=tk.X)
        
        # Initial update of processing list
        self._update_processing_list()
    
    def _update_processing_list(self):
        """Update the processing list based on selected options"""
        # Clear existing list
        for widget in self.processing_list_frame.winfo_children():
            widget.destroy()
        
        # Always show client videos first
        if self.data.client_videos:
            ttk.Label(self.processing_list_frame, 
                     text=f"✓ {len(self.data.client_videos)} client video(s) from Google Drive",
                     style='Body.TLabel', font=('Segoe UI', 9),
                     foreground=self.theme.colors['success']).pack(anchor=tk.W, padx=20, pady=1)
        
        # Show transition/stitching option based on checkbox
        if self.use_transitions.get():
            # When transitions are ENABLED
            ttk.Label(self.processing_list_frame,
                     text="✓ Fade in-out transitions",
                     style='Body.TLabel', font=('Segoe UI', 9),
                     foreground=self.theme.colors['success']).pack(anchor=tk.W, padx=20, pady=1)
        else:
            # When transitions are DISABLED
            ttk.Label(self.processing_list_frame,
                     text="✓ Basic stitching (no transitions)",
                     style='Body.TLabel', font=('Segoe UI', 9),
                     foreground=self.theme.colors['success']).pack(anchor=tk.W, padx=20, pady=1)
        
        # Show quiz outro WITHOUT any transition text
        if hasattr(self.data, 'templates_to_add'):
            # Just show "Add quiz outro" without checking template text
            quiz_shown = False
            for template in self.data.templates_to_add:
                if not quiz_shown and 'quiz' in template.lower():
                    ttk.Label(self.processing_list_frame, 
                             text="✓ Add quiz outro (Facebook/Quiz)",
                             style='Body.TLabel', font=('Segoe UI', 9),
                             foreground=self.theme.colors['success']).pack(anchor=tk.W, padx=20, pady=1)
                    quiz_shown = True
                    break
    
    def _add_output_location(self, parent):
        """Add output location section"""
        self.output_section_frame = ttk.Frame(parent, style='White.TFrame')
        self.output_section_frame.pack(fill=tk.X, pady=(0, 10))  # REDUCED from (0, 15)
        
        ttk.Label(self.output_section_frame, text="Output Location:", style='Body.TLabel',
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 4))  # REDUCED from (0, 6)
        
        self.output_frame = ttk.Frame(self.output_section_frame, style='White.TFrame')
        self.output_frame.pack(fill=tk.X, padx=20)
        
        ttk.Label(self.output_frame, text="📁", font=('Segoe UI', 14),  # Was 16
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        
        # Get output file name from data
        output_text = self.data.output_location if hasattr(self.data, 'output_location') else "Project folder"
        self.output_label = ttk.Label(self.output_frame, text=output_text, style='Body.TLabel',
                                     font=('Segoe UI', 9), foreground='#666666')
        self.output_label.pack(side=tk.LEFT)  # Was 10
        
        # Auto-process note
        ttk.Label(self.output_section_frame, text="Processing will complete automatically",
                 style='Body.TLabel', font=('Segoe UI', 8, 'italic'),  # Was 9
                 foreground='#888888').pack(anchor=tk.W, padx=20, pady=(5, 0))
    
    def _refresh_output_location(self):
        """Refresh the output location display when project name changes"""
        if hasattr(self, 'output_label') and hasattr(self.data, 'output_location'):
            self.output_label.config(text=self.data.output_location)
    
    def _on_confirm(self):
        """Handle confirm button click"""
        print(f"✅ Confirmation tab: Confirm clicked")
        
        # Store transition setting in orchestrator if available
        if self.orchestrator:
            self.orchestrator.use_transitions = self.use_transitions.get()
            print(f"   Transitions enabled: {self.orchestrator.use_transitions}")
        
        # Call dialog controller's confirm method
        if self.dialog_controller:
            self.dialog_controller._on_confirm()
    
    def _on_cancel(self):
        """Handle cancel button click"""
        print(f"❌ Confirmation tab: Cancel clicked")
        if self.dialog_controller:
            self.dialog_controller._on_cancel()