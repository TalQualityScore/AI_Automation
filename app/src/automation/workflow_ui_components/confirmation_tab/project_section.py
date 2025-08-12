# app/src/automation/workflow_ui_components/confirmation_tab/project_section.py
"""
UPDATED Project Information Section
Replace single processing dropdown with multi-select checkboxes
MINIMAL CHANGES to existing file structure
"""

import tkinter as tk
from tkinter import ttk

class ProjectSection:
    """Project information section with multi-select processing modes"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        
        # NEW: Multi-select processing mode variables
        self.mode_vars = {}
        self._init_mode_vars()
        
        self.create_section()
    
    def _init_mode_vars(self):
        """Initialize checkbox variables for multi-select"""
        mode_options = [
            "save_only",
            "quiz_only", 
            "vsl_only",
            "svsl_only",
            "connector_quiz",
            "connector_vsl",
            "connector_svsl"
        ]
        
        for mode in mode_options:
            self.mode_vars[mode] = tk.BooleanVar()
        
        # Set initial selection based on detected mode
        current_mode = getattr(self.data, 'processing_mode', 'quiz_only')
        if current_mode in self.mode_vars:
            self.mode_vars[current_mode].set(True)
            print(f"✅ Pre-selected mode: {current_mode}")
    
    def create_section(self):
        """Create project info section - UNCHANGED structure"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Project name field (unchanged)
        self._create_project_field(section_frame)
        
        # Account dropdown (unchanged)
        self._create_account_dropdown(section_frame)
        
        # Platform dropdown (unchanged)
        self._create_platform_dropdown(section_frame)
        
        # CHANGED: Multi-select processing mode section
        self._create_processing_mode_multiselect(section_frame)
        
        # Info note (unchanged)
        self._create_info_note(section_frame)
    
    def _create_project_field(self, parent):
        """Create project name field - UNCHANGED"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Label(info_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=14).pack(side=tk.LEFT)
        
        self.main_tab.project_name_var.set(self.data.project_name)
        self.main_tab.project_name_entry = ttk.Entry(
            info_frame, 
            textvariable=self.main_tab.project_name_var,
            font=('Segoe UI', 10, 'bold'), 
            width=37
        )
        self.main_tab.project_name_entry.pack(side=tk.LEFT)
        self.main_tab.project_name_entry.bind('<KeyRelease>', self._on_project_name_change)
    
    def _create_account_dropdown(self, parent):
        """Create account dropdown - UNCHANGED"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Label(info_frame, text="Account:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=14).pack(side=tk.LEFT)
        
        self.main_tab.account_var.set(self._get_default_account_selection())
        account_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.main_tab.account_var,
            values=self._get_account_options(),
            font=('Segoe UI', 10), 
            width=35, 
            state='readonly'
        )
        account_combo.pack(side=tk.LEFT)
        account_combo.bind('<<ComboboxSelected>>', lambda e: self._safe_account_change())
    
    def _create_platform_dropdown(self, parent):
        """Create platform dropdown - UNCHANGED"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Label(info_frame, text="Platform:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=14).pack(side=tk.LEFT)
        
        self.main_tab.platform_var.set(self._get_default_platform_selection())
        platform_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.main_tab.platform_var,
            values=self._get_platform_options(),
            font=('Segoe UI', 10), 
            width=35, 
            state='readonly'
        )
        platform_combo.pack(side=tk.LEFT)
        platform_combo.bind('<<ComboboxSelected>>', self._on_platform_change)
    
    def _create_processing_mode_multiselect(self, parent):
        """NEW: Create multi-select processing mode section"""
        # Header
        header_frame = ttk.Frame(parent, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(header_frame, text="Processing:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=14).pack(side=tk.LEFT)
        
        ttk.Label(header_frame, text="(Select one or more)", style='Body.TLabel',
                 font=('Segoe UI', 9), foreground='gray').pack(side=tk.LEFT)
        
        # Checkbox container
        checkbox_frame = ttk.Frame(parent, style='White.TFrame')
        checkbox_frame.pack(fill=tk.X, padx=(110, 0))  # Indent to align with other fields
        
        # Create checkboxes in two columns
        left_column = ttk.Frame(checkbox_frame, style='White.TFrame')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_column = ttk.Frame(checkbox_frame, style='White.TFrame')
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mode options with display names
        mode_options = [
            ("save_only", "Save As Is"),
            ("quiz_only", "Add Quiz Outro"),
            ("vsl_only", "Add VSL"),
            ("svsl_only", "Add SVSL"),
            ("connector_quiz", "Add Connector + Quiz"),
            ("connector_vsl", "Add Connector + VSL"),
            ("connector_svsl", "Add Connector + SVSL")
        ]
        
        # Distribute checkboxes across columns
        for i, (mode_code, display_name) in enumerate(mode_options):
            target_column = left_column if i < 4 else right_column
            
            checkbox = ttk.Checkbutton(
                target_column,
                text=display_name,
                variable=self.mode_vars[mode_code],
                style='Body.TCheckbutton',
                command=lambda: self._on_processing_mode_change()
            )
            checkbox.pack(anchor=tk.W, pady=1)
    
    def _create_info_note(self, parent):
        """Create info note - UNCHANGED"""
        note_frame = ttk.Frame(parent, style='White.TFrame')
        note_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(note_frame, text="💡 All fields above can be edited to override auto-detection",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                 foreground='#605e5c').pack()
    
    # NEW: Multi-select helper methods
    def get_selected_processing_modes(self) -> list:
        """Get list of currently selected processing modes"""
        selected = []
        for mode_code, var in self.mode_vars.items():
            if var.get():
                selected.append(mode_code)
        
        # Ensure at least one mode is selected
        if not selected:
            self.mode_vars['save_only'].set(True)
            selected = ['save_only']
            print("⚠️ No modes selected, defaulting to Save As Is")
        
        return selected
    
    def set_selected_processing_modes(self, modes: list):
        """Set selected processing modes programmatically"""
        # Clear all selections
        for var in self.mode_vars.values():
            var.set(False)
        
        # Set specified modes
        for mode in modes:
            if mode in self.mode_vars:
                self.mode_vars[mode].set(True)
        
        print(f"✅ Processing modes set to: {modes}")
    
    # All existing helper methods - UNCHANGED
    def _get_account_options(self):
        """Get CORRECT account options from actual config.py - UNCHANGED"""
        return [
            "TR - Total Restore",
            "BC3 - Bio Complete 3",
            "OO - Olive Oil",
            "MCT - MCT",
            "DS - Dark Spot",
            "NB - Nature's Blend",
            "MK - Morning Kick",
            "DRC - Dermal Repair Complex",
            "PC - Phyto Collagen",
            "GD - Glucose Defense",
            "MC - Morning Complete",
            "PP - Pro Plant",
            "SPC - Superfood Complete",
            "MA - Metabolic Advanced",
            "KA - Keto Active",
            "BLR - BadLand Ranch",
            "Bio X4 - Bio X4",
            "Upwellness - Upwellness"
        ]
    
    def _get_platform_options(self):
        """Platform options - UNCHANGED"""
        return [
            "FB - Facebook",
            "YT - YouTube",
            "IG - Instagram", 
            "TT - TikTok",
            "SNAP - Snapchat"
        ]
    
    def _get_default_account_selection(self):
        """Get default account selection - UNCHANGED"""
        current_account = getattr(self.data, 'account', 'TR')
        
        print(f"DEBUG: Looking for account code: {current_account}")
        
        for option in self._get_account_options():
            if option.startswith(current_account + ' - '):
                print(f"DEBUG: Found matching account: {option}")
                return option
        
        print(f"DEBUG: No match found, using default TR - Total Restore")
        return "TR - Total Restore"
    
    def _get_default_platform_selection(self):
        """Get default platform selection - UNCHANGED"""
        current_platform = getattr(self.data, 'platform', 'FB')
        
        print(f"DEBUG: Looking for platform code: {current_platform}")
        
        for option in self._get_platform_options():
            if option.startswith(current_platform + ' - '):
                print(f"DEBUG: Found matching platform: {option}")
                return option
        
        return "FB - Facebook"
    
    def _on_project_name_change(self, event=None):
        """Handle project name changes - UNCHANGED"""
        new_name = self.main_tab.project_name_var.get()
        if new_name != self.data.project_name:
            print(f"📝 Project name changed: '{self.data.project_name}' → '{new_name}'")
            old_name = self.data.project_name
            self.data.project_name = new_name
            
            if hasattr(self.data, 'output_location'):
                self.data.output_location = self.data.output_location.replace(old_name, new_name)
                self.main_tab.refresh_output_location()
    
    def _safe_account_change(self):
        """Safe account change handler - UNCHANGED"""
        try:
            selected = self.main_tab.account_var.get()
            if selected and ' - ' in selected:
                account_code = selected.split(' - ')[0]
                print(f"🔄 Account changed to: {account_code}")
                
                self.data.account = account_code
                self.main_tab.refresh_summary()
        except Exception as e:
            print(f"⚠️ Account change error (safely handled): {e}")
    
    def _on_platform_change(self, event=None):
        """Handle platform change - UNCHANGED"""
        selected = self.main_tab.platform_var.get()
        if selected and ' - ' in selected:
            platform_code = selected.split(' - ')[0]
            print(f"🔄 Platform changed to: {platform_code}")
            
            self.data.platform = platform_code
            self.main_tab.refresh_summary()
    
    def _on_processing_mode_change(self, event=None):
        """UPDATED: Handle processing mode changes (now multi-select)"""
        selected_modes = self.get_selected_processing_modes()
        print(f"🔄 Processing modes changed to: {selected_modes}")
        
        # Update data object with first selected mode for compatibility
        if selected_modes:
            self.data.processing_mode = selected_modes[0]
        
        # Store all selected modes
        self.data.selected_processing_modes = selected_modes
        
        # Refresh summary
        self.main_tab.refresh_summary()