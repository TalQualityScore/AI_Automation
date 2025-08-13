# app/src/automation/workflow_ui_components/confirmation_tab/main_tab.py
"""
UPDATED Main Confirmation Tab Controller
Add multi-mode support to existing file
MINIMAL CHANGES to existing structure
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List
from ...workflow_data_models import ConfirmationData, ValidationIssue

from .project_section import ProjectSection
from .summary_section import SummarySection
from .validation_section import ValidationSection
from .video_section import VideoSection
from .processing_section import ProcessingSection
from .output_section import OutputSection

class ConfirmationTab:
    """Main confirmation tab controller with multi-mode support"""
    
    def __init__(self, parent: ttk.Frame, data, theme):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.orchestrator = None
        self.dialog_controller = None
        
        # State variables - UNCHANGED
        self.use_transitions = tk.BooleanVar(value=True)
        
        # Keep existing dropdown variables for backward compatibility
        self.account_var = tk.StringVar()
        self.platform_var = tk.StringVar()
        self.processing_mode_var = tk.StringVar()  # Keep for compatibility
        self.project_name_var = tk.StringVar()
        
        # Section controllers
        self.sections = {}
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference - UNCHANGED"""
        self.orchestrator = orchestrator
        print(f"✅ ConfirmationTab: Orchestrator reference set")
    
    def set_dialog_controller(self, controller):
        """Set dialog controller reference - UNCHANGED"""
        self.dialog_controller = controller
        print(f"✅ ConfirmationTab: Dialog controller reference set")
    
    def get_updated_data(self):
        """UPDATED: Get the current confirmation data with multi-mode selections"""
        # Update basic fields - UNCHANGED
        if hasattr(self, 'project_name_var'):
            self.data.project_name = self.project_name_var.get()
        
        # Capture dropdown selections - UNCHANGED
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
        
        # NEW: Capture multi-mode selections from project section
        if 'project' in self.sections and hasattr(self.sections['project'], 'get_selected_processing_modes'):
            selected_modes = self.sections['project'].get_selected_processing_modes()
            # For backward compatibility, set the first mode as primary
            self.data.processing_mode = selected_modes[0] if selected_modes else "save_only"
            # Store all selected modes
            self.data.selected_processing_modes = selected_modes
            print(f"🔄 Multi-mode selection captured: {selected_modes}")
        
        return self.data
    
    def get_selected_processing_modes(self) -> List[str]:
        """NEW: Get list of selected processing modes"""
        if 'project' in self.sections and hasattr(self.sections['project'], 'get_selected_processing_modes'):
            return self.sections['project'].get_selected_processing_modes()
        
        # Fallback to single mode for backward compatibility
        return [getattr(self.data, 'processing_mode', 'save_only')]
    
    def _get_mode_code_from_display(self, display_text):
        """Convert display text back to mode code - UNCHANGED"""
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
        """Get the current transition setting - UNCHANGED"""
        return self.use_transitions.get()
    
    def create_tab(self):
        """Create and return the tab frame - UNCHANGED"""
        if not hasattr(self, 'frame'):
            self.frame = ttk.Frame(self.parent, style='White.TFrame')
            self._create_ui_in_frame(self.frame)
        return self.frame
    
    def _create_ui_in_frame(self, parent_frame):
        """Create confirmation UI with modular sections - UNCHANGED"""
        main_frame = ttk.Frame(parent_frame, style='White.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(20, 100))
        
        content_frame = ttk.Frame(main_frame, style='White.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_sections(content_frame)
        print("✅ Multi-mode confirmation tab created")
    
    def _create_sections(self, parent):
        """Create all sections in order - UNCHANGED"""
        # 1. Project Information Section (now with multi-select)
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
        """UPDATED: Refresh summary section with multi-mode support"""
        print("DEBUG: refresh_summary() called")
        try:
            if hasattr(self, 'sections') and 'summary' in self.sections:
                # Get selected modes for summary
                selected_modes = self.get_selected_processing_modes()
                
                if hasattr(self.sections['summary'], 'refresh_with_modes'):
                    print(f"DEBUG: Calling summary.refresh_with_modes({selected_modes})")
                    self.sections['summary'].refresh_with_modes(selected_modes)
                    print("DEBUG: Multi-mode summary section refreshed successfully")
                elif hasattr(self.sections['summary'], 'refresh'):
                    print("DEBUG: Calling summary.refresh()")
                    self.sections['summary'].refresh()
                    print("DEBUG: Summary section refreshed successfully")
                else:
                    print("DEBUG: Summary section doesn't have refresh method")
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
        """Refresh output location when project name changes - UNCHANGED"""
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
        """Handle cancel button click - UNCHANGED"""
        if self.dialog_controller:
            self.dialog_controller._on_cancel()
        else:
            print("WARNING: No dialog controller set")

    def _on_confirm(self):
        """UPDATED: Handle confirm button click with multi-mode validation"""
        if self.dialog_controller:
            # NEW: Validate multi-mode selection
            selected_modes = self.get_selected_processing_modes()
            if not selected_modes:
                print("❌ No processing modes selected")
                return
            
            # Get transition setting
            use_transitions = self.use_transitions.get()
            self.dialog_controller.dialog.use_transitions = use_transitions
            
            print(f"🎬 Starting multi-mode processing: {selected_modes}")
            print(f"🎬 Transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
            
            # Call the dialog's confirm handler
            self.dialog_controller._on_confirm()
        else:
            print("WARNING: No dialog controller set")
    
    def validate_data(self) -> list[ValidationIssue]:
        """UPDATED: Validate current configuration including multi-mode"""
        issues = []
        
        # Basic validation - UNCHANGED
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
        
        # NEW: Multi-mode validation
        selected_modes = self.get_selected_processing_modes()
        if not selected_modes:
            issues.append(ValidationIssue(
                level="error",
                message="At least one processing mode must be selected",
                field="processing_modes"
            ))
        
        # Check for conflicting combinations
        has_connector = any('connector' in mode for mode in selected_modes)
        has_individual = any(mode.endswith('_only') for mode in selected_modes)
        
        if has_connector and has_individual:
            issues.append(ValidationIssue(
                level="warning",
                message="Connector modes and individual modes selected - this may create duplicate processing",
                field="processing_modes"
            ))
        
        if not hasattr(self.data, 'output_folder') or not self.data.output_folder:
            issues.append(ValidationIssue(
                level="warning",
                message="Output folder not specified - will use default location",
                field="output_folder"
            ))
        
        return issues
    
    def refresh_data(self, new_data: ConfirmationData):
        """Refresh tab with new data - UNCHANGED"""
        self.data = new_data
        
        if hasattr(self, 'sections'):
            for section_name, section in self.sections.items():
                if hasattr(section, 'refresh_data'):
                    section.refresh_data(new_data)
        
        print(f"DEBUG: Confirmation tab refreshed with new data")

    def on_processing_modes_changed(self, selected_modes):
        """Handle when processing modes are changed in project section"""
        print(f"🔄 Processing modes changed to: {selected_modes}")
        
        # Update the data
        self.data.selected_processing_modes = selected_modes
        self.data.processing_mode = selected_modes[0] if selected_modes else "save_only"
        
        # Refresh the summary section
        if 'summary' in self.sections and hasattr(self.sections['summary'], 'refresh_with_modes'):
            self.sections['summary'].refresh_with_modes(selected_modes)
        
        # Refresh the output section
        if 'output' in self.sections and hasattr(self.sections['output'], 'refresh_with_modes'):
            self.sections['output'].refresh_with_modes(selected_modes)
    
    def get_current_settings(self) -> dict:
        """UPDATED: Get current user settings including multi-mode"""
        selected_modes = self.get_selected_processing_modes()
        
        settings = {
            'project_name': self.project_name_var.get() if hasattr(self, 'project_name_var') else self.data.project_name,
            'account': self.account_var.get() if hasattr(self, 'account_var') else getattr(self.data, 'account', ''),
            'platform': self.platform_var.get() if hasattr(self, 'platform_var') else getattr(self.data, 'platform', ''),
            'processing_mode': selected_modes[0] if selected_modes else 'save_only',  # First mode for compatibility
            'selected_processing_modes': selected_modes,  # NEW: All selected modes
            'use_transitions': self.use_transitions.get() if hasattr(self, 'use_transitions') else True
        }
        
        return settings