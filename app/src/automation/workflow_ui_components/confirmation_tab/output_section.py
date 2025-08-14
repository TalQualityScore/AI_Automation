# app/src/automation/workflow_ui_components/confirmation_tab/output_section.py
"""
Output Location Section - COMPLETE CORRECTED VERSION
Shows where the processed videos will be saved - ENHANCED for multi-mode
FIXED: Title preservation when refreshing modes
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
        self.title_label = None
        # Bound variables for state stability
        self.folder_count_var = tk.StringVar()
        self.folder_list_vars = []  # List of StringVars for folder paths
        self.create_section()
    
    def create_section(self):
        """Create output location section - ENHANCED for multi-mode"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create and store reference to title label
        self.title_label = ttk.Label(section_frame, text="📁 Output Location", 
                                   style='Body.TLabel', font=('Segoe UI', 11, 'bold'))
        self.title_label.pack(anchor=tk.W)
        
        # Check for actually selected modes (from checkboxes), not detected modes
        selected_modes = self._get_selected_modes()
        
        # ALWAYS render N outputs for N modes (including N=1)
        self._create_multi_mode_display(section_frame, selected_modes)
    
    def _get_selected_modes(self):
        """Get currently selected processing modes"""
        selected_modes = []
        
        # Try to get the actual selections from project section
        if hasattr(self.main_tab, 'sections') and 'project' in self.main_tab.sections:
            project_section = self.main_tab.sections['project']
            if hasattr(project_section, 'get_selected_processing_modes'):
                selected_modes = project_section.get_selected_processing_modes()
        
        # If no selections yet, fall back to single mode
        if not selected_modes:
            selected_modes = [getattr(self.data, 'processing_mode', 'save_only')]
        
        return selected_modes
    
    def update_folder_count_only(self, selected_modes):
        """Update only the folder count without clearing other output details"""
        print(f"🔄 Updating folder count for {len(selected_modes)} modes")
        
        # Find and update the multi-mode label if it exists
        if hasattr(self, 'parent') and self.parent:
            for widget in self.parent.winfo_children():
                try:
                    widget_text = widget.cget('text') if hasattr(widget, 'cget') else ""
                    if "Multi-Mode Processing:" in widget_text or "folders will be created" in widget_text:
                        # Update the folder count
                        new_text = f"🔄 Multi-Mode Processing: {len(selected_modes)} folders will be created"
                        widget.config(text=new_text)
                        print(f"✅ Updated folder count to {len(selected_modes)}")
                        return
                except:
                    pass
        
        print(f"⚠️ Could not find folder count label to update")
    
    def _create_multi_mode_display(self, parent, selected_modes):
        """Create output display for N modes using bound variables for state stability"""
        # Mode count indicator with bound variable (works for 1+ modes)
        multi_label = ttk.Label(
            parent,
            textvariable=self.folder_count_var,
            style='Body.TLabel',
            font=('Segoe UI', 10),
            foreground='#0078d4'
        )
        multi_label.pack(anchor=tk.W, padx=(15, 0), pady=(5, 5))
        
        # Create folder labels with bound variables (up to reasonable max)
        max_folders = 10  # Reasonable maximum for UI
        for i in range(max_folders):
            if len(self.folder_list_vars) <= i:
                self.folder_list_vars.append(tk.StringVar())
            
            mode_label = ttk.Label(
                parent,
                textvariable=self.folder_list_vars[i],
                style='Body.TLabel',
                font=('Segoe UI', 9),
                foreground='#605e5c'
            )
            mode_label.pack(anchor=tk.W, padx=(15, 0))
        
        # Initialize bound variables with current data
        if len(selected_modes) == 1:
            count_text = f"🔄 Processing: 1 folder will be created"
        else:
            count_text = f"🔄 Multi-Mode Processing: {len(selected_modes)} folders will be created"
        self.folder_count_var.set(count_text)
        
        # Initialize folder list vars
        for i, mode in enumerate(selected_modes):
            mode_suffix = self._get_mode_suffix(mode)
            project_name = getattr(self.data, 'project_name', 'Project')
            # Handle empty suffix for save_only mode
            if mode_suffix.strip():
                folder_name = f"{project_name} {mode_suffix}"
            else:
                folder_name = project_name.strip()
            folder_text = f"• Output/{folder_name}/"
            
            if len(self.folder_list_vars) <= i:
                self.folder_list_vars.append(tk.StringVar())
            self.folder_list_vars[i].set(folder_text)
    
    def _get_mode_suffix(self, mode):
        """Get appropriate suffix for mode"""
        mode_suffixes = {
            'quiz_only': 'Quiz',
            'vsl_only': 'VSL',
            'svsl_only': 'SVSL',
            'connector_quiz': 'Connector Quiz',
            'connector_vsl': 'Connector VSL',
            'connector_svsl': 'Connector SVSL',
            'save_only': ''  # No suffix for save_only
        }
        return mode_suffixes.get(mode, mode.upper())
    
    def refresh(self):
        """Refresh output location display"""
        if self.output_location_label:
            location_text = getattr(self.data, 'output_location', 'Will be determined during processing')
            self.output_location_label.config(text=location_text)

    def refresh_with_modes(self, selected_modes):
        """IDEMPOTENT: Update output display using bound variables (no widget destroy)"""
        print(f"🔄 Refreshing output display for {len(selected_modes)} modes (idempotent)")
        
        # Update folder count via bound variable (ALWAYS for N modes)
        if len(selected_modes) == 1:
            count_text = f"🔄 Processing: 1 folder will be created"
        else:
            count_text = f"🔄 Multi-Mode Processing: {len(selected_modes)} folders will be created"
        self.folder_count_var.set(count_text)
        
        # Update folder list via bound variables (ALWAYS for N modes)
        for i, mode in enumerate(selected_modes):
            mode_suffix = self._get_mode_suffix(mode)
            project_name = getattr(self.data, 'project_name', 'Project')
            # Handle empty suffix for save_only mode
            if mode_suffix.strip():
                folder_name = f"{project_name} {mode_suffix}"
            else:
                folder_name = project_name.strip()
            folder_text = f"• Output/{folder_name}/"
            
            # Ensure we have enough StringVars
            while len(self.folder_list_vars) <= i:
                self.folder_list_vars.append(tk.StringVar())
            
            self.folder_list_vars[i].set(folder_text)
        
        # Clear unused folder vars
        for i in range(len(selected_modes), len(self.folder_list_vars)):
            self.folder_list_vars[i].set("")
        
        print(f"✅ Output display updated via bound variables - no widget destruction")
        
        # Update data
        self.data.selected_processing_modes = selected_modes
        
        # Create appropriate display based on selected modes
        if len(selected_modes) > 1:
            # Multi-mode display
            self._create_multi_mode_display(self.parent, selected_modes)
        else:
            # Single mode display
            if selected_modes:
                mode_suffix = self._get_mode_suffix(selected_modes[0])
                project_name = getattr(self.data, 'project_name', 'Project')
                # Handle empty suffix for save_only mode
                if mode_suffix.strip():
                    location_text = f"Output/{project_name} {mode_suffix}/"
                else:
                    location_text = f"Output/{project_name}/"
            else:
                location_text = "Will be determined during processing"
            
            # Create single mode label
            self.output_location_label = ttk.Label(
                self.parent, 
                text=location_text,
                style='Body.TLabel', 
                font=('Segoe UI', 9),
                foreground='#605e5c'
            )
            self.output_location_label.pack(anchor=tk.W, padx=(15, 0))
        
        print(f"✅ Output location refreshed with {len(selected_modes)} modes - title preserved")
    
    def refresh_data(self, new_data):
        """Refresh section with new data"""
        self.data = new_data
        self.refresh()