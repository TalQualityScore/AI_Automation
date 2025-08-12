# app/src/automation/workflow_ui_components/confirmation_tab/main_tab.py
"""
Main Confirmation Tab Controller
Modular architecture with organized sections
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from ...workflow_data_models import ConfirmationData, ValidationIssue

from .project_section import ProjectSection
from .summary_section import SummarySection
from .validation_section import ValidationSection
from .video_section import VideoSection
from .processing_section import ProcessingSection
from .output_section import OutputSection

class ConfirmationTab:
    """Main confirmation tab controller - Modular architecture"""
    
    def __init__(self, parent: ttk.Frame, data, theme):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.orchestrator = None
        self.dialog_controller = None
        
        # State variables
        self.use_transitions = tk.BooleanVar(value=True)
        
        # NEW: Dropdown variables for user selections
        self.account_var = tk.StringVar()
        self.platform_var = tk.StringVar()
        self.processing_mode_var = tk.StringVar()
        self.project_name_var = tk.StringVar()
        
        # Section controllers
        self.sections = {}
        
        # UI will be created later by create_tab() when TabManager needs it
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference"""
        self.orchestrator = orchestrator
        print(f"✅ ConfirmationTab: Orchestrator reference set")
    
    def set_dialog_controller(self, controller):
        """Set dialog controller reference"""
        self.dialog_controller = controller
        print(f"✅ ConfirmationTab: Dialog controller reference set")
    
    def get_updated_data(self):
        """Get the current confirmation data with user selections"""
        # Update the data with current values from all fields
        if hasattr(self, 'project_name_var'):
            self.data.project_name = self.project_name_var.get()
        
        # NEW: Capture dropdown selections
        if hasattr(self, 'account_var'):
            selected_account = self.account_var.get()
            if selected_account and ' - ' in selected_account:
                account_code = selected_account.split(' - ')[0]
                self.data.account = account_code
                print(f"🔄 Account selection captured: {account_code}")
        
        if hasattr(self, 'platform_var'):
            selected_platform = self.platform_var.get()
            if selected_platform and ' - ' in selected_platform:
                platform_code = selected_platform.split(' - ')[0]
                self.data.platform = platform_code
                print(f"🔄 Platform selection captured: {platform_code}")
        
        if hasattr(self, 'processing_mode_var'):
            selected_mode = self.processing_mode_var.get()
            if selected_mode:
                mode_code = self._get_mode_code_from_display(selected_mode)
                self.data.processing_mode = mode_code
                print(f"🔄 Processing mode selection captured: {mode_code}")
        
        return self.data
    
    def _get_mode_code_from_display(self, display_text):
        """Convert display text back to mode code"""
        mode_mapping = {
            "Save As Is": "save_only",
            "Add Quiz Outro": "quiz_only", 
            "Add Connector + Quiz": "connector_quiz",
            "Add SVSL": "svsl_only",
            "Add Connector + SVSL": "connector_svsl",
            "Add VSL": "vsl_only",
            "Add Connector + VSL": "connector_vsl"
        }
        return mode_mapping.get(display_text, display_text.lower().replace(' ', '_'))
    
    def get_transition_setting(self):
        """Get the current transition setting"""
        return self.use_transitions.get()
    
    def create_tab(self):
        """Create and return the tab frame - MODULAR VERSION"""
        if not hasattr(self, 'frame'):
            self.frame = ttk.Frame(self.parent, style='White.TFrame')
            self._create_ui_in_frame(self.frame)
        return self.frame
    
    def _create_ui_in_frame(self, parent_frame):
        """Create confirmation UI with modular sections"""
        # Main scrollable frame
        main_frame = ttk.Frame(parent_frame, style='White.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Create scrollable area
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0, height=500)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='White.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Better mousewheel binding
        def _on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        
        # Content sections
        content_frame = ttk.Frame(scrollable_frame, style='White.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 20))
        
        # Initialize and create all sections
        self._create_sections(content_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ADD BUTTONS DIRECTLY HERE
        self._create_action_buttons(parent_frame)

    def _create_action_buttons(self, parent_frame):
        """Create action buttons at the bottom of the confirmation tab"""
        # Create button frame at the bottom of the parent frame
        button_frame = ttk.Frame(parent_frame, style='White.TFrame')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=40, pady=(10, 20))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_container, 
            text="❌ CANCEL", 
            style='Secondary.TButton',
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Confirm button
        confirm_btn = ttk.Button(
            button_container, 
            text="✅ CONFIRM & RUN", 
            style='Accent.TButton', 
            command=self._on_confirm
        )
        confirm_btn.pack(side=tk.LEFT)
        confirm_btn.focus_set()
        
        # Store reference
        self.button_frame = button_frame
        
        print("DEBUG: Buttons created in confirmation tab")
        print(f"DEBUG: Button frame visible: {button_frame.winfo_viewable()}")

    def _on_cancel(self):
        """Handle cancel button click"""
        if self.dialog_controller:
            self.dialog_controller._on_cancel()
        else:
            print("WARNING: No dialog controller set")

    def _on_confirm(self):
        """Handle confirm button click"""
        if self.dialog_controller:
            # Get transition setting
            use_transitions = self.use_transitions.get()
            self.dialog_controller.dialog.use_transitions = use_transitions
            print(f"🎬 Starting processing with transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
            
            # Call the dialog's confirm handler
            self.dialog_controller._on_confirm()
        else:
            print("WARNING: No dialog controller set")
    
    def _create_sections(self, content_frame):
        """Create all modular sections - FIXED ORDER"""
        # Project Info Section (with dropdowns)
        self.sections['project'] = ProjectSection(
            content_frame, self.data, self.theme, self
        )
        
        # Validation Section
        self.sections['validation'] = ValidationSection(
            content_frame, self.data, self.theme, self
        )
        
        # REMOVED: Video Info Section - redundant with Processing Summary
        # self.sections['video'] = VideoSection(
        #     content_frame, self.data, self.theme, self
        # )
        
        # Processing Options BEFORE Summary
        self.sections['processing'] = ProcessingSection(
            content_frame, self.data, self.theme, self
        )
        
        # Summary Section (includes video count)
        self.sections['summary'] = SummarySection(
            content_frame, self.data, self.theme, self
        )
        
        # Output Location Section
        self.sections['output'] = OutputSection(
            content_frame, self.data, self.theme, self
        )
    
    def refresh_summary(self):
        """Refresh summary section when settings change"""
        if 'summary' in self.sections:
            self.sections['summary'].refresh()
    
    def refresh_output_location(self):
        """Refresh output location when project name changes"""
        if 'output' in self.sections:
            self.sections['output'].refresh()