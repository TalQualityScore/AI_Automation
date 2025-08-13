# app/src/automation/workflow_ui_components/confirmation_tab/output_section.py
"""
Output Location Section
Shows where the processed videos will be saved - ENHANCED for multi-mode
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
        """Create output location section - ENHANCED for multi-mode"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(section_frame, text="📁 Output Location", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # Check for actually selected modes (from checkboxes), not detected modes
        # First check if user has made selections, otherwise check detected
        selected_modes = []
        
        # Try to get the actual selections from project section
        if hasattr(self.main_tab, 'sections') and 'project' in self.main_tab.sections:
            project_section = self.main_tab.sections['project']
            if hasattr(project_section, 'get_selected_processing_modes'):
                selected_modes = project_section.get_selected_processing_modes()
        
        # If no selections yet, fall back to single mode
        if not selected_modes:
            selected_modes = [getattr(self.data, 'processing_mode', 'save_only')]
        
        if len(selected_modes) > 1:
            # Multi-mode display
            self._create_multi_mode_display(section_frame, selected_modes)
        else:
            # Single-mode display (existing logic)
            location_text = getattr(self.data, 'output_location', 'Will be determined during processing')
            self.output_location_label = ttk.Label(
                section_frame, 
                text=location_text,
                style='Body.TLabel', 
                font=('Segoe UI', 9),
                foreground='#605e5c'
            )
            self.output_location_label.pack(anchor=tk.W, padx=(15, 0))
    
    def _create_multi_mode_display(self, parent, selected_modes):
        """NEW: Create multi-mode output display"""
        # Multi-mode indicator
        multi_label = ttk.Label(
            parent,
            text=f"🔄 Multi-Mode Processing: {len(selected_modes)} folders will be created",
            style='Body.TLabel',
            font=('Segoe UI', 10),
            foreground='#0078d4'
        )
        multi_label.pack(anchor=tk.W, padx=(15, 0), pady=(5, 5))
        
        # Show each mode that will be processed
        for i, mode in enumerate(selected_modes, 1):
            mode_suffix = self._get_mode_suffix(mode)
            project_name = getattr(self.data, 'project_name', 'Project')
            folder_name = f"{project_name} {mode_suffix}"
            
            mode_label = ttk.Label(
                parent,
                text=f"  {i}. Output/{folder_name}/",
                style='Body.TLabel',
                font=('Segoe UI', 9),
                foreground='#605e5c'
            )
            mode_label.pack(anchor=tk.W, padx=(30, 0))
    
    def _get_mode_suffix(self, mode):
        """Get appropriate suffix for mode"""
        mode_suffixes = {
            'quiz_only': 'Quiz',
            'vsl_only': 'VSL',
            'svsl_only': 'SVSL',
            'connector_quiz': 'Connector Quiz',
            'connector_vsl': 'Connector VSL',
            'connector_svsl': 'Connector SVSL',
            'save_only': 'Original'
        }
        return mode_suffixes.get(mode, mode.upper())
    
    def refresh(self):
        """Refresh output location display"""
        if self.output_location_label:
            location_text = getattr(self.data, 'output_location', 'Will be determined during processing')
            self.output_location_label.config(text=location_text)

    def refresh_with_modes(self, selected_modes):
        """Refresh output display when modes change"""
        # Clear all widgets in parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Recreate the title
        ttk.Label(self.parent, text="📁 Output Location", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # Update data
        self.data.selected_processing_modes = selected_modes
        
        # Create appropriate display
        if len(selected_modes) > 1:
            self._create_multi_mode_display(self.parent, selected_modes)
        else:
            # Single mode or no mode
            if selected_modes:
                mode_suffix = self._get_mode_suffix(selected_modes[0])
                project_name = getattr(self.data, 'project_name', 'Project')
                if mode_suffix and mode_suffix != 'Original':
                    location_text = f"Output/{project_name} {mode_suffix}/"
                else:
                    location_text = f"Output/{project_name}/"
            else:
                location_text = "Will be determined during processing"
            
            self.output_location_label = ttk.Label(
                self.parent, 
                text=location_text,
                style='Body.TLabel', 
                font=('Segoe UI', 9),
                foreground='#605e5c'
            )
            self.output_location_label.pack(anchor=tk.W, padx=(15, 0))