# app/src/automation/workflow_ui_components/confirmation_tab/project_section/mode_selector.py
"""
Mode Selector - Multi-Mode Selection UI
Handles the complex multi-mode selection dropdown interface
"""

import tkinter as tk

class ModeSelector:
    """Handles multi-mode selection UI and logic"""
    
    def __init__(self, project_section):
        self.ps = project_section
        self.mode_dropdown_frame = None
        self.mode_button = None
        self.mode_menu = None
        self.menu_visible = False
        
        # Mode configuration
        self.mode_options = [
            ("save_only", "Save As Is"),
            ("quiz_only", "Add Quiz Outro"),
            ("vsl_only", "Add VSL"),
            ("svsl_only", "Add SVSL"),
            ("connector_quiz", "Add Connector + Quiz"),
            ("connector_vsl", "Add Connector + VSL"),
            ("connector_svsl", "Add Connector + SVSL")
        ]
    
    def init_mode_vars(self):
        """Initialize checkbox variables for multi-select"""
        mode_vars = {}
        
        # Create BooleanVar for each mode option
        for mode_code, _ in self.mode_options:
            mode_vars[mode_code] = tk.BooleanVar()
        
        # Check if multi-mode was detected
        detected_modes = getattr(self.ps.data, 'detected_modes', None)
        selected_modes = getattr(self.ps.data, 'selected_processing_modes', None)
        
        if selected_modes and len(selected_modes) > 1:
            # Multi-mode detected - check all detected modes
            for mode in selected_modes:
                if mode in mode_vars:
                    mode_vars[mode].set(True)
            print(f"✅ Pre-selected modes: {selected_modes}")
        else:
            # Single mode - only check the one mode
            current_mode = getattr(self.ps.data, 'processing_mode', 'quiz_only')
            if current_mode in mode_vars:
                mode_vars[current_mode].set(True)
                print(f"✅ Pre-selected mode: {current_mode}")
        
        return mode_vars
    
    def create_multiselect_ui(self, parent):
        """Create the dropdown-style multi-select processing mode UI"""
        # Create a frame that looks like a dropdown
        self.mode_dropdown_frame = tk.Frame(parent, bg='white')
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
        
        print("✅ Multi-mode selector UI created")
    
    def _get_mode_display_text(self):
        """Get display text for selected modes"""
        selected = self.get_selected_processing_modes()
        
        if not selected:
            return "(Select one or more)"
        elif len(selected) == 1:
            # Find display name for single mode
            for mode_code, display_name in self.mode_options:
                if mode_code == selected[0]:
                    return display_name
            return selected[0]
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
        
        # Add title
        title_frame = tk.Frame(menu_frame, bg='#f0f0f0')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="Select Processing Modes:",
            font=('Segoe UI', 9, 'bold'),
            bg='#f0f0f0',
            fg='#323130'
        )
        title_label.pack(pady=3)
        
        # Add checkboxes for each mode option
        for mode_code, display_name in self.mode_options:
            cb_frame = tk.Frame(menu_frame, bg='white')
            cb_frame.pack(fill=tk.X, padx=5, pady=2)
            
            cb = tk.Checkbutton(
                cb_frame,
                text=display_name,
                variable=self.ps.mode_vars[mode_code],
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
        
        # Bind events to close menu
        self.mode_menu.bind("<FocusOut>", lambda e: self._hide_mode_menu())
        self.mode_menu.bind("<Escape>", lambda e: self._hide_mode_menu())
        
        print("✅ Mode selection menu displayed")
    
    def _hide_mode_menu(self):
        """Hide the mode selection menu"""
        if self.mode_menu:
            self.mode_menu.destroy()
            self.mode_menu = None
        self.menu_visible = False
        print("✅ Mode selection menu hidden")
    
    def _on_mode_selection_change(self):
        """Handle mode selection change"""
        # Update button text
        self.mode_button.config(text=self._get_mode_display_text())
        
        # Get selected modes
        selected_modes = self.get_selected_processing_modes()
        print(f"🔄 Mode selection changed: {selected_modes}")
        
        # Notify main tab to refresh other sections
        if hasattr(self.ps.main_tab, 'on_processing_modes_changed'):
            self.ps.main_tab.on_processing_modes_changed(selected_modes)
    
    def get_selected_processing_modes(self):
        """Get list of currently selected processing modes"""
        selected = []
        for mode_code, var in self.ps.mode_vars.items():
            if var.get():
                selected.append(mode_code)
        
        # Ensure at least one mode is selected
        if not selected:
            self.ps.mode_vars['save_only'].set(True)
            selected = ['save_only']
            print("⚠️ No modes selected, defaulting to Save As Is")
        
        return selected
    
    def set_selected_processing_modes(self, modes):
        """Set selected processing modes programmatically"""
        print(f"🔧 Setting processing modes to: {modes}")
        
        # Clear all selections
        for var in self.ps.mode_vars.values():
            var.set(False)
        
        # Set specified modes
        for mode in modes:
            if mode in self.ps.mode_vars:
                self.ps.mode_vars[mode].set(True)
                print(f"✅ Mode '{mode}' selected")
            else:
                print(f"⚠️ Unknown mode '{mode}' ignored")
        
        # Update button display if UI exists
        if self.mode_button:
            self.mode_button.config(text=self._get_mode_display_text())
        
        print(f"✅ Processing modes set to: {modes}")
    
    def get_mode_display_name(self, mode_code):
        """Get display name for mode code"""
        for code, display_name in self.mode_options:
            if code == mode_code:
                return display_name
        return mode_code.replace('_', ' ').title()
    
    def get_mode_code_from_display(self, display_name):
        """Get mode code from display name"""
        for code, display in self.mode_options:
            if display == display_name:
                return code
        return display_name.lower().replace(' ', '_')
    
    def validate_mode(self, mode_code):
        """Validate if mode code is supported"""
        return mode_code in [code for code, _ in self.mode_options]
    
    def get_all_mode_codes(self):
        """Get list of all supported mode codes"""
        return [code for code, _ in self.mode_options]
    
    def get_all_mode_displays(self):
        """Get list of all mode display names"""
        return [display for _, display in self.mode_options]