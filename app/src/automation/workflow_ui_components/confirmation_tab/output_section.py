# app/src/automation/workflow_ui_components/confirmation_tab/output_section.py
"""
ENHANCED Output Location Section
Shows multiple output paths when multiple processing modes are selected
BASED ON YOUR EXISTING FILE - ADDED multi-mode display logic
"""

import tkinter as tk
from tkinter import ttk

class OutputSection:
    """Output location section with multi-mode support"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.output_location_label = None
        self.output_container = None  # NEW: Container for dynamic content
        self.create_section()
    
    def create_section(self):
        """Create output location section"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(section_frame, text="📁 Output Location", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # NEW: Create container for dynamic content instead of fixed label
        self.output_container = ttk.Frame(section_frame, style='White.TFrame')
        self.output_container.pack(fill=tk.X, padx=(15, 0))
        
        # Initial display
        self._update_output_display()
    
    def _update_output_display(self):
        """NEW: Update the output display based on selected modes"""
        # Clear existing content
        for widget in self.output_container.winfo_children():
            widget.destroy()
        
        # Get selected processing modes
        selected_modes = self._get_selected_modes()
        
        if len(selected_modes) <= 1:
            # Single mode display - same as before
            self._display_single_output(selected_modes)
        else:
            # Multi-mode display - NEW functionality
            self._display_multi_output(selected_modes)
    
    def _get_selected_modes(self):
        """Get currently selected processing modes"""
        if hasattr(self.main_tab, 'get_selected_processing_modes'):
            return self.main_tab.get_selected_processing_modes()
        
        # Fallback to single mode
        return [getattr(self.data, 'processing_mode', 'save_only')]
    
    def _display_single_output(self, selected_modes):
        """Display single output location - enhanced from original"""
        mode = selected_modes[0] if selected_modes else 'save_only'
        
        # Get base location - enhanced to build proper path
        base_location = getattr(self.data, 'output_location', 'Desktop')
        if base_location == 'Will be determined during processing':
            base_location = 'Desktop'
        
        project_name = getattr(self.data, 'project_name', 'Unknown Project')
        
        # Build folder name with mode
        mode_display = self._get_mode_display(mode)
        if mode_display != 'Save As Is':  # Don't add mode suffix for save as is
            folder_name = f"GH {project_name} {mode_display}"
        else:
            folder_name = f"GH {project_name}"
        
        full_path = f"{base_location}\\{folder_name}"
        
        # Create label (same as original but in container)
        self.output_location_label = ttk.Label(
            self.output_container,
            text=full_path,
            style='Body.TLabel',
            font=('Segoe UI', 9),
            foreground='#605e5c'
        )
        self.output_location_label.pack(anchor=tk.W)
    
    def _display_multi_output(self, selected_modes):
        """NEW: Display multiple output locations for multi-mode"""
        # Header text
        header_label = ttk.Label(
            self.output_container,
            text=f"{len(selected_modes)} separate folders will be created:",
            style='Body.TLabel',
            font=('Segoe UI', 9),
            foreground='#605e5c'
        )
        header_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Get base info
        base_location = getattr(self.data, 'output_location', 'Desktop')
        if base_location == 'Will be determined during processing':
            base_location = 'Desktop'
        
        project_name = getattr(self.data, 'project_name', 'Unknown Project')
        
        # Display each mode's output path
        for i, mode in enumerate(selected_modes, 1):
            mode_display = self._get_mode_display(mode)
            folder_name = f"GH {project_name} {mode_display}"
            full_path = f"{base_location}\\{folder_name}"
            
            # Create indented label for each path
            path_label = ttk.Label(
                self.output_container,
                text=f"  {i}. {full_path}",
                style='Body.TLabel',
                font=('Segoe UI', 8),
                foreground='#605e5c'
            )
            path_label.pack(anchor=tk.W)
    
    def _get_mode_display(self, mode):
        """Get display name for processing mode"""
        mode_displays = {
            "save_only": "Save As Is",
            "quiz_only": "Quiz",
            "connector_quiz": "Connector Quiz",
            "svsl_only": "SVSL",
            "connector_svsl": "Connector SVSL",
            "vsl_only": "VSL",
            "connector_vsl": "Connector VSL"
        }
        return mode_displays.get(mode, mode.replace('_', ' ').title())
    
    def refresh(self):
        """ENHANCED: Refresh output location display - now handles multi-mode"""
        self._update_output_display()
    
    def refresh_location(self):
        """Alias for refresh method for compatibility"""
        self.refresh()