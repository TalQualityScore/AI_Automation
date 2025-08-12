# app/src/automation/workflow_ui_components/confirmation_tab/project_section.py
"""
Project Information Section
Handles project name, account, platform, and processing mode dropdowns
"""

import tkinter as tk
from tkinter import ttk

class ProjectSection:
    """Project information section with dropdowns"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.create_section()
    
    def create_section(self):
        """Create project info section with dropdowns"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Project name field
        self._create_project_field(section_frame)
        
        # Account dropdown
        self._create_account_dropdown(section_frame)
        
        # Platform dropdown
        self._create_platform_dropdown(section_frame)
        
        # Processing mode dropdown
        self._create_processing_mode_dropdown(section_frame)
        
        # Info note
        self._create_info_note(section_frame)
    
    def _create_project_field(self, parent):
        """Create project name field"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Label(info_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=14).pack(side=tk.LEFT)
        
        # Project name entry with correct width
        self.main_tab.project_name_var.set(self.data.project_name)
        self.main_tab.project_name_entry = ttk.Entry(
            info_frame, 
            textvariable=self.main_tab.project_name_var,
            font=('Segoe UI', 10, 'bold'), 
            width=37  # Matches dropdown width
        )
        self.main_tab.project_name_entry.pack(side=tk.LEFT)
        self.main_tab.project_name_entry.bind('<KeyRelease>', self._on_project_name_change)
    
    def _create_account_dropdown(self, parent):
        """Create account dropdown with safe binding"""
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
        # Safe binding to prevent crashes
        account_combo.bind('<<ComboboxSelected>>', lambda e: self._safe_account_change())
    
    def _create_platform_dropdown(self, parent):
        """Create platform dropdown"""
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
    
    def _create_processing_mode_dropdown(self, parent):
        """Create processing mode dropdown"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Label(info_frame, text="Processing:", style='Body.TLabel',
                 font=('Segoe UI', 10), width=14).pack(side=tk.LEFT)
        
        self.main_tab.processing_mode_var.set(self._get_default_processing_mode_selection())
        mode_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.main_tab.processing_mode_var,
            values=self._get_processing_mode_options(),
            font=('Segoe UI', 10), 
            width=35, 
            state='readonly'
        )
        mode_combo.pack(side=tk.LEFT)
        mode_combo.bind('<<ComboboxSelected>>', self._on_processing_mode_change)
    
    def _create_info_note(self, parent):
        """Create info note about overrides"""
        note_frame = ttk.Frame(parent, style='White.TFrame')
        note_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(note_frame, text="💡 All fields above can be edited to override auto-detection",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                 foreground='#605e5c').pack()
    
    def _get_account_options(self):
        """Get CORRECT account options from actual config.py"""
        # CORRECTED: Using actual account names from your GitHub config.py
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
        """Platform options"""
        return [
            "FB - Facebook",
            "YT - YouTube",
            "IG - Instagram", 
            "TT - TikTok",
            "SNAP - Snapchat"
        ]
    
    def _get_processing_mode_options(self):
        """Processing mode options"""
        return [
            "Save As Is",
            "Add Quiz Outro",
            "Add Connector + Quiz", 
            "Add SVSL",
            "Add Connector + SVSL",
            "Add VSL",
            "Add Connector + VSL"
        ]
    
    def _get_default_account_selection(self):
        """Get default account selection - match what's detected"""
        current_account = getattr(self.data, 'account', 'TR')
        
        print(f"DEBUG: Looking for account code: {current_account}")
        
        # Find matching account in options
        for option in self._get_account_options():
            if option.startswith(current_account + ' - '):
                print(f"DEBUG: Found matching account: {option}")
                return option
        
        # Default fallback
        print(f"DEBUG: No match found, using default TR - Total Restore")
        return "TR - Total Restore"
    
    def _get_default_platform_selection(self):
        """Get default platform selection"""
        current_platform = getattr(self.data, 'platform', 'FB')
        
        print(f"DEBUG: Looking for platform code: {current_platform}")
        
        for option in self._get_platform_options():
            if option.startswith(current_platform + ' - '):
                print(f"DEBUG: Found matching platform: {option}")
                return option
        
        return "FB - Facebook"
    
    def _get_default_processing_mode_selection(self):
        """Get default processing mode selection"""
        current_mode = getattr(self.data, 'processing_mode', 'quiz_only')
        
        print(f"DEBUG: Current processing mode: {current_mode}")
        
        mode_displays = {
            "save_only": "Save As Is",
            "quiz_only": "Add Quiz Outro", 
            "connector_quiz": "Add Connector + Quiz",
            "svsl_only": "Add SVSL",
            "connector_svsl": "Add Connector + SVSL", 
            "vsl_only": "Add VSL",
            "connector_vsl": "Add Connector + VSL"
        }
        
        result = mode_displays.get(current_mode, "Add Quiz Outro")
        print(f"DEBUG: Selected processing mode: {result}")
        return result
    
    def _on_project_name_change(self, event=None):
        """Handle project name changes"""
        new_name = self.main_tab.project_name_var.get()
        if new_name != self.data.project_name:
            print(f"📝 Project name changed: '{self.data.project_name}' → '{new_name}'")
            old_name = self.data.project_name
            self.data.project_name = new_name
            
            # Update output location
            if hasattr(self.data, 'output_location'):
                self.data.output_location = self.data.output_location.replace(old_name, new_name)
                self.main_tab.refresh_output_location()
    
    def _safe_account_change(self):
        """Safe account change handler"""
        try:
            selected = self.main_tab.account_var.get()
            if selected and ' - ' in selected:
                account_code = selected.split(' - ')[0]
                print(f"🔄 Account changed to: {account_code}")
                
                # Update the data object
                self.data.account = account_code
                
                # Refresh summary
                self.main_tab.refresh_summary()
        except Exception as e:
            print(f"⚠️ Account change error (safely handled): {e}")
    
    def _on_platform_change(self, event=None):
        """Handle platform change"""
        selected = self.main_tab.platform_var.get()
        if selected and ' - ' in selected:
            platform_code = selected.split(' - ')[0]
            print(f"🔄 Platform changed to: {platform_code}")
            
            # Update the data object
            self.data.platform = platform_code
            
            # Refresh summary
            self.main_tab.refresh_summary()
    
    def _on_processing_mode_change(self, event=None):
        """Handle processing mode change"""
        selected = self.main_tab.processing_mode_var.get()
        
        # Convert display name back to code
        mode_map = {
            "Save As Is": "save_only",
            "Add Quiz Outro": "quiz_only",
            "Add Connector + Quiz": "connector_quiz",
            "Add SVSL": "svsl_only",
            "Add Connector + SVSL": "connector_svsl",
            "Add VSL": "vsl_only",
            "Add Connector + VSL": "connector_vsl"
        }
        
        mode_code = mode_map.get(selected, "quiz_only")
        print(f"🔄 Processing mode changed to: {mode_code}")
        
        # Update the data object
        self.data.processing_mode = mode_code
        
        # Refresh summary
        self.main_tab.refresh_summary()