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
        
        # Check if multi-mode was detected
        detected_modes = getattr(self.data, 'detected_modes', None)
        selected_modes = getattr(self.data, 'selected_processing_modes', None)
        
        if selected_modes and len(selected_modes) > 1:
            # Multi-mode detected - check all detected modes
            for mode in selected_modes:
                if mode in self.mode_vars:
                    self.mode_vars[mode].set(True)
            print(f"✅ Pre-selected modes: {selected_modes}")
        else:
            # Single mode - only check the one mode
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
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
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
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
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
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
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
        """Create dropdown-style multi-select processing mode section"""
        # Header
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(info_frame, text="Processing:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=10).pack(side=tk.LEFT)
        
        # Create a frame that looks like a dropdown
        self.mode_dropdown_frame = ttk.Frame(info_frame, style='White.TFrame')
        self.mode_dropdown_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create the dropdown button
        self.mode_button = tk.Button(
            self.mode_dropdown_frame,
            text=self._get_mode_display_text(),
            font=('Segoe UI', 10),
            bg='white',
            fg='black',
            bd=1,
            relief='solid',
            anchor='w',
            padx=5,
            width=35,
            command=self._toggle_mode_dropdown
        )
        self.mode_button.pack(side=tk.LEFT)
        
        # Create dropdown arrow
        arrow_label = tk.Label(
            self.mode_dropdown_frame,
            text="▼",
            font=('Segoe UI', 8),
            bg='white',
            fg='gray'
        )
        arrow_label.place(relx=0.95, rely=0.5, anchor='e')
        
        # Create the dropdown menu (initially hidden)
        self.mode_menu = None
        self.menu_visible = False
        
    def _get_mode_display_text(self):
        """Get display text for selected modes"""
        selected = self.get_selected_processing_modes()
        if not selected:
            return "(Select one or more)"
        elif len(selected) == 1:
            mode_names = {
                'save_only': 'Save As Is',
                'quiz_only': 'Add Quiz Outro',
                'vsl_only': 'Add VSL',
                'svsl_only': 'Add SVSL',
                'connector_quiz': 'Connector + Quiz',
                'connector_vsl': 'Connector + VSL',
                'connector_svsl': 'Connector + SVSL'
            }
            return mode_names.get(selected[0], selected[0])
        else:
            return f"{len(selected)} modes selected"
    
    def _toggle_mode_dropdown(self):
        """Toggle the dropdown menu visibility"""
        if self.menu_visible:
            self._hide_mode_menu()
        else:
            self._show_mode_menu()
    
    def _show_mode_menu(self):
        """Show the mode selection menu"""
        if self.mode_menu:
            self.mode_menu.destroy()
        
        # Create dropdown window
        self.mode_menu = tk.Toplevel(self.mode_button)
        self.mode_menu.wm_overrideredirect(True)
        
        # Position below button
        x = self.mode_button.winfo_rootx()
        y = self.mode_button.winfo_rooty() + self.mode_button.winfo_height()
        self.mode_menu.geometry(f"+{x}+{y}")
        
        # Create menu frame
        menu_frame = tk.Frame(self.mode_menu, bg='white', bd=1, relief='solid')
        menu_frame.pack()
        
        # Add checkboxes
        mode_options = [
            ("save_only", "Save As Is"),
            ("quiz_only", "Add Quiz Outro"),
            ("vsl_only", "Add VSL"),
            ("svsl_only", "Add SVSL"),
            ("connector_quiz", "Add Connector + Quiz"),
            ("connector_vsl", "Add Connector + VSL"),
            ("connector_svsl", "Add Connector + SVSL")
        ]
        
        for mode_code, display_name in mode_options:
            cb_frame = tk.Frame(menu_frame, bg='white')
            cb_frame.pack(fill=tk.X, padx=5, pady=2)
            
            cb = tk.Checkbutton(
                cb_frame,
                text=display_name,
                variable=self.mode_vars[mode_code],
                bg='white',
                font=('Segoe UI', 9),
                anchor='w',
                command=self._on_mode_selection_change
            )
            cb.pack(fill=tk.X)
        
        # Add close button
        close_frame = tk.Frame(menu_frame, bg='#f0f0f0')
        close_frame.pack(fill=tk.X, pady=(5, 0))
        
        close_btn = tk.Button(
            close_frame,
            text="Done",
            font=('Segoe UI', 9),
            bg='#0078d4',
            fg='white',
            bd=0,
            padx=10,
            pady=3,
            command=self._hide_mode_menu
        )
        close_btn.pack(pady=3)
        
        self.menu_visible = True
        
        # Bind click outside to close
        self.mode_menu.bind("<FocusOut>", lambda e: self._hide_mode_menu())
    
    def _hide_mode_menu(self):
        """Hide the mode selection menu"""
        if self.mode_menu:
            self.mode_menu.destroy()
            self.mode_menu = None
        self.menu_visible = False
    
    def _on_mode_selection_change(self):
        """Handle mode selection change"""
        # Update button text
        self.mode_button.config(text=self._get_mode_display_text())
        
        # Get selected modes
        selected_modes = self.get_selected_processing_modes()
        
        # Notify main tab to refresh other sections
        if hasattr(self.main_tab, 'on_processing_modes_changed'):
            self.main_tab.on_processing_modes_changed(selected_modes)
    
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