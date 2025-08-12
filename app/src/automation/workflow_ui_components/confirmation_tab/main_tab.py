# app/src/automation/workflow_ui_components/confirmation_tab/main_tab.py
"""
Main Confirmation Tab Controller - FIXED: No scrolling + Working refresh methods
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
        """Create and return the tab frame - FIXED VERSION WITHOUT SCROLLING"""
        if not hasattr(self, 'frame'):
            self.frame = ttk.Frame(self.parent, style='White.TFrame')
            self._create_ui_in_frame(self.frame)
        return self.frame
    
    def _create_ui_in_frame(self, parent_frame):
        """Create confirmation UI with modular sections - FIXED: No scrolling"""
        # REMOVED: All scrolling components (Canvas, Scrollbar, etc.)
        # Main container - simple frame without scrolling
        main_frame = ttk.Frame(parent_frame, style='White.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(20, 100))  # Added bottom padding for buttons
        
        # Content sections - direct frame, no scrolling needed
        content_frame = ttk.Frame(main_frame, style='White.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize and create all sections
        self._create_sections(content_frame)
        
        print("DEBUG: Fixed confirmation tab created without scrolling")
    
    def _create_sections(self, parent):
        """Create all sections in order - FIXED: Correct constructor calls"""
        # 1. Project Information Section - Fixed constructor call
        self.sections['project'] = ProjectSection(
            parent, self.data, self.theme, self
        )
        
        # 2. Validation Section (only if needed)
        if hasattr(self.data, 'issues') and self.data.issues:
            self.sections['validation'] = ValidationSection(
                parent, self.data, self.theme, self
            )
        
        # 3. Processing Options Section  
        self.sections['processing'] = ProcessingSection(
            parent, self.data, self.theme, self
        )
        
        # 4. Processing Summary Section
        self.sections['summary'] = SummarySection(
            parent, self.data, self.theme, self
        )
        
        # 5. Output Location Section
        self.sections['output'] = OutputSection(
            parent, self.data, self.theme, self
        )
        
        print("DEBUG: All confirmation sections created successfully")
    
    def refresh_summary(self):
        """Refresh summary section when settings change - FIXED WITH DEBUGGING"""
        print("DEBUG: refresh_summary() called")
        try:
            if hasattr(self, 'sections') and 'summary' in self.sections:
                if hasattr(self.sections['summary'], 'refresh'):
                    print("DEBUG: Calling summary.refresh()")
                    self.sections['summary'].refresh()
                    print("DEBUG: Summary section refreshed successfully")
                else:
                    print("DEBUG: Summary section doesn't have refresh method")
                    # Force recreate the summary content
                    if hasattr(self.sections['summary'], '_update_summary_content'):
                        self.sections['summary']._update_summary_content()
                        print("DEBUG: Summary content updated directly")
            else:
                print("DEBUG: No summary section found in sections")
        except Exception as e:
            print(f"DEBUG: Error in refresh_summary: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_output_location(self):
        """Refresh output location when project name changes - FIXED WITH DEBUGGING"""
        print("DEBUG: refresh_output_location() called")
        try:
            if hasattr(self, 'sections') and 'output' in self.sections:
                if hasattr(self.sections['output'], 'refresh'):
                    print("DEBUG: Calling output.refresh()")
                    self.sections['output'].refresh()
                    print("DEBUG: Output section refreshed successfully")
                else:
                    print("DEBUG: Output section doesn't have refresh method")
            else:
                print("DEBUG: No output section found in sections")
        except Exception as e:
            print(f"DEBUG: Error in refresh_output_location: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def validate_data(self) -> list[ValidationIssue]:
        """Validate current configuration"""
        issues = []
        
        # Basic validation
        if not self.data.project_name or self.data.project_name.strip() == "":
            issues.append(ValidationIssue(
                level="error",
                message="Project name is required",
                field="project_name"
            ))
        
        if not hasattr(self.data, 'account') or not self.data.account:
            issues.append(ValidationIssue(
                level="error", 
                message="Account selection is required",
                field="account"
            ))
        
        if not hasattr(self.data, 'platform') or not self.data.platform:
            issues.append(ValidationIssue(
                level="error",
                message="Platform selection is required", 
                field="platform"
            ))
        
        if not hasattr(self.data, 'client_videos') or len(self.data.client_videos) == 0:
            issues.append(ValidationIssue(
                level="error",
                message="At least one client video is required",
                field="client_videos"
            ))
        
        # Check for missing output folder
        if not hasattr(self.data, 'output_folder') or not self.data.output_folder:
            issues.append(ValidationIssue(
                level="warning",
                message="Output folder not specified - will use default location",
                field="output_folder"
            ))
        
        return issues
    
    def refresh_data(self, new_data: ConfirmationData):
        """Refresh tab with new data"""
        self.data = new_data
        
        # Update section data if sections exist
        if hasattr(self, 'sections'):
            for section_name, section in self.sections.items():
                if hasattr(section, 'refresh_data'):
                    section.refresh_data(new_data)
        
        print(f"DEBUG: Confirmation tab refreshed with new data")
    
    def get_current_settings(self) -> dict:
        """Get current user settings from all sections"""
        settings = {
            'project_name': self.project_name_var.get() if hasattr(self, 'project_name_var') else self.data.project_name,
            'account': self.account_var.get() if hasattr(self, 'account_var') else getattr(self.data, 'account', ''),
            'platform': self.platform_var.get() if hasattr(self, 'platform_var') else getattr(self.data, 'platform', ''),
            'processing_mode': self.processing_mode_var.get() if hasattr(self, 'processing_mode_var') else getattr(self.data, 'processing_mode', ''),
            'use_transitions': self.use_transitions.get() if hasattr(self, 'use_transitions') else True
        }
        
        return settings