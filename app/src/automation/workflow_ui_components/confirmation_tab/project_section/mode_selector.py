# app/src/automation/workflow_ui_components/confirmation_tab/project_section/mode_selector.py
"""
Mode Selector - Multi-Mode Selection UI
Handles the complex multi-mode selection dropdown interface
"""

import tkinter as tk
from tkinter import ttk

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
        # Create ttk.Combobox for perfect visual parity with Account/Platform
        # Use bound variable for state management
        if not hasattr(self.ps.main_tab, 'processing_display_var'):
            self.ps.main_tab.processing_display_var = tk.StringVar()
        
        self.mode_combo = ttk.Combobox(
            parent,
            textvariable=self.ps.main_tab.processing_display_var,
            font=('Segoe UI', 10),
            state='readonly',
            values=()  # Empty values to prevent native dropdown
        )
        # Grid with sticky=ew for right-edge alignment matching other fields
        self.mode_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(5, 0))
        
        # Set initial display text and bind click handlers
        self._update_display_text()
        # Prevent native dropdown completely and use our custom window
        self.mode_combo.bind('<Button-1>', self._on_combobox_click)
        self.mode_combo.bind('<Down>', lambda e: 'break')  # Prevent arrow key dropdown  
        self.mode_combo.bind('<Up>', lambda e: 'break')    # Prevent arrow key dropdown
        self.mode_combo.bind('<space>', lambda e: 'break') # Prevent spacebar dropdown
        self.mode_combo.bind('<Return>', lambda e: 'break') # Prevent enter dropdown
        self.mode_combo.bind('<<ComboboxSelected>>', lambda e: 'break')  # Prevent selection
        self.mode_combo.bind('<FocusIn>', lambda e: 'break')  # Prevent focus dropdown
        
        print("✅ Multi-mode selector UI created")
        print(f"🔧 Combobox state: {self.mode_combo['state']}")
        print(f"🔧 Combobox has focus: {self.mode_combo == self.mode_combo.focus_get()}")
        
        # Test if the combobox responds to events
        def test_click(e):
            print("🧪 TEST: Direct click event detected on combobox!")
        self.mode_combo.bind('<ButtonPress-1>', test_click, '+')
    
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
    
    def _update_display_text(self):
        """Update the display text in the bound variable"""
        if hasattr(self.ps.main_tab, 'processing_display_var'):
            self.ps.main_tab.processing_display_var.set(self._get_mode_display_text())
    
    def _on_combobox_click(self, event=None):
        """Handle combobox click to show multi-select menu"""
        print(f"🖱️ Processing dropdown clicked! Menu visible: {self.menu_visible}")
        try:
            self._toggle_mode_dropdown()
            print("✅ Toggle completed")
        except Exception as e:
            print(f"❌ Error in combobox click: {e}")
            import traceback
            traceback.print_exc()
        return 'break'  # Prevent native dropdown
    
    def _toggle_mode_dropdown(self):
        """Toggle the dropdown menu visibility"""
        print(f"🔄 Toggling dropdown. Current state: visible={self.menu_visible}")
        if self.menu_visible:
            print("🔻 Hiding menu...")
            self._hide_mode_menu()
        else:
            print("🔺 Showing menu...")
            self._show_mode_menu()
    
    def _show_mode_menu(self):
        """Show the mode selection menu"""
        # Ensure only ONE custom window exists
        if self.mode_menu and hasattr(self.mode_menu, 'winfo_exists'):
            try:
                if self.mode_menu.winfo_exists():
                    self.mode_menu.lift()
                    return
            except:
                pass
        
        # Create dropdown window
        self.mode_menu = tk.Toplevel(self.mode_combo)
        
        # Remove window decorations to make it look like a dropdown
        self.mode_menu.wm_overrideredirect(True)
        
        # Make it transient and grab focus for safety
        self.mode_menu.transient(self.mode_combo.winfo_toplevel())
        
        # Set window properties for proper dropdown behavior
        self.mode_menu.resizable(False, False)
        
        print(f"🔧 Toplevel window created: {self.mode_menu}")
        
        # SIMPLEST APPROACH: Force proper positioning after window creation
        # Let everything render first
        self.mode_menu.update()
        
        # Use a callback to set position after the GUI loop processes
        def set_position():
            try:
                # Get screen position of combobox - try the direct approach one more time
                combo_screen_x = self.mode_combo.winfo_rootx()
                combo_screen_y = self.mode_combo.winfo_rooty()
                combo_width = self.mode_combo.winfo_width() 
                combo_height = self.mode_combo.winfo_height()
                
                # Position dropdown directly below combobox
                dropdown_x = combo_screen_x
                dropdown_y = combo_screen_y + combo_height + 2
                dropdown_width = max(combo_width, 200)
                
                print(f"🔧 DELAYED POSITIONING:")
                print(f"🔧 Combo screen pos: x={combo_screen_x}, y={combo_screen_y}")
                print(f"🔧 Combo size: w={combo_width}, h={combo_height}")
                print(f"🔧 Setting dropdown to: x={dropdown_x}, y={dropdown_y}")
                
                # Get actual menu height and apply geometry
                menu_height = menu_frame.winfo_reqheight()
                geometry_str = f"{dropdown_width}x{menu_height}+{dropdown_x}+{dropdown_y}"
                self.mode_menu.geometry(geometry_str)
                self.mode_menu.lift()
                print(f"🔧 Applied final geometry: {geometry_str}")
                
            except Exception as e:
                print(f"❌ Error in delayed positioning: {e}")
        
        # Schedule the positioning for after the current event loop
        self.mode_combo.after(1, set_position)
        
        combo_width = 200  # Use default width for initial setup
        dropdown_width = 200
        
        # Create menu frame that fills the window exactly
        menu_frame = tk.Frame(self.mode_menu, bg='white', bd=1, relief='solid')
        menu_frame.pack(fill=tk.BOTH, expand=False, anchor=tk.N)  # Don't expand to prevent extra space
        
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
        
        # Add selectable options (blue background style instead of checkboxes)
        self.option_frames = {}  # Store frames for background color changes
        
        for mode_code, display_name in self.mode_options:
            # Debug: Check if mode variable exists
            if mode_code not in self.ps.mode_vars:
                print(f"⚠️ Missing mode variable for {mode_code}")
                self.ps.mode_vars[mode_code] = tk.BooleanVar()
            
            # Create frame for each option
            option_frame = tk.Frame(menu_frame, bg='white', cursor='hand2')
            option_frame.pack(fill=tk.X, padx=2, pady=1)
            self.option_frames[mode_code] = option_frame
            
            # Create label for the option text
            option_label = tk.Label(
                option_frame,
                text=display_name,
                bg='white',
                font=('Segoe UI', 9),
                anchor='w',
                padx=10,
                pady=4,
                cursor='hand2'
            )
            option_label.pack(fill=tk.X)
            
            # Bind click events to both frame and label
            def make_click_handler(mode):
                def handle_click(event=None):
                    self._toggle_option_selection(mode)
                return handle_click
            
            click_handler = make_click_handler(mode_code)
            option_frame.bind("<Button-1>", click_handler)
            option_label.bind("<Button-1>", click_handler)
            
            # Set initial visual state
            self._update_option_visual_state(mode_code)
            
            print(f"✅ Option created for {mode_code}: {display_name}")
        
        # Add close button with tight spacing to eliminate white space
        close_frame = tk.Frame(menu_frame, bg='#f0f0f0')
        close_frame.pack(fill=tk.X, pady=(5, 0))  # No bottom padding
        
        close_btn = tk.Button(
            close_frame,
            text="Done",
            font=('Segoe UI', 9),
            bg='#0078d4',
            fg='white',
            bd=0,
            padx=10,
            pady=2,  # Reduced vertical padding
            command=self._hide_mode_menu
        )
        close_btn.pack(pady=(2, 2))  # Minimal padding to frame edges
        
        self.menu_visible = True
        
        # Initial geometry - the callback will set the correct position
        self.mode_menu.update_idletasks()
        menu_height = menu_frame.winfo_reqheight()
        initial_geometry = f"{dropdown_width}x{menu_height}+100+100"  # Temporary position
        self.mode_menu.geometry(initial_geometry)
        
        print(f"🔧 Initial geometry set: {initial_geometry}")
        print(f"🔧 Menu frame height: {menu_height}")
        print("🔧 Delayed positioning callback scheduled...")
        
        # The proper position will be set by the callback
        self.mode_menu.lift()
        
        print(f"🔧 Dropdown will be repositioned shortly")
        
        # DON'T use grab_set() - it freezes the entire UI
        # Instead rely on click detection and focus events
        
        # Bind events to close menu (multiple ways to ensure it can always be closed)
        self.mode_menu.bind("<FocusOut>", lambda e: self._hide_mode_menu())
        self.mode_menu.bind("<Escape>", lambda e: self._hide_mode_menu())
        self.mode_menu.bind("<Return>", lambda e: self._hide_mode_menu())
        
        # DON'T bind click events to the menu window - let checkboxes handle their own clicks
        
        # Also bind to root window to detect clicks outside
        root = self.mode_combo.winfo_toplevel()
        root.bind("<Button-1>", self._check_click_outside, "+")
        
        print("✅ Mode selection menu displayed")
    
    def _check_click_outside(self, event):
        """Check if click is outside the dropdown menu to close it"""
        try:
            # Only process if menu is visible
            if not self.menu_visible or not self.mode_menu:
                return
            
            # Get click coordinates relative to screen
            click_x, click_y = event.x_root, event.y_root
            
            # Get menu window bounds
            menu_x = self.mode_menu.winfo_rootx()
            menu_y = self.mode_menu.winfo_rooty()
            menu_width = self.mode_menu.winfo_width()
            menu_height = self.mode_menu.winfo_height()
            
            # Check if click is outside menu bounds
            outside_x = click_x < menu_x or click_x > menu_x + menu_width
            outside_y = click_y < menu_y or click_y > menu_y + menu_height
            
            # Also check if click is on the combobox itself (keep menu open)
            combo_x = self.mode_combo.winfo_rootx()
            combo_y = self.mode_combo.winfo_rooty()
            combo_width = self.mode_combo.winfo_width()
            combo_height = self.mode_combo.winfo_height()
            
            on_combo_x = combo_x <= click_x <= combo_x + combo_width
            on_combo_y = combo_y <= click_y <= combo_y + combo_height
            
            # Only close if click is TRULY outside both menu and combobox
            # Don't close on clicks inside the menu (let checkboxes work)
            if (outside_x or outside_y) and not (on_combo_x and on_combo_y):
                # Double-check this isn't a checkbox click by checking target widget
                if hasattr(event, 'widget') and event.widget:
                    widget_class = event.widget.__class__.__name__
                    if widget_class in ['Checkbutton', 'Button']:
                        print(f"🔘 Click on {widget_class} - keeping menu open")
                        return
                
                print("🔒 Click detected outside menu - closing")
                self._hide_mode_menu()
                
        except Exception as e:
            print(f"⚠️ Error in click outside detection: {e}")
    
    def _hide_mode_menu(self):
        """Hide the mode selection menu with proper cleanup"""
        if self.mode_menu:
            try:
                # Set menu as not visible FIRST (this makes _check_click_outside ignore events)
                self.menu_visible = False
                
                # Destroy window (no grab to release since we don't use grab_set)
                self.mode_menu.destroy()
                self.mode_menu = None
                
            except Exception as e:
                print(f"⚠️ Error during menu cleanup: {e}")
                self.mode_menu = None
        
        # Ensure menu is marked as not visible
        self.menu_visible = False
        print("✅ Mode selection menu hidden with proper cleanup")
    
    def _toggle_option_selection(self, mode_code):
        """Toggle selection state for an option (blue background style)"""
        try:
            print(f"🔘 Option clicked for mode: {mode_code}")
            
            # Toggle the boolean variable
            if mode_code in self.ps.mode_vars:
                current_state = self.ps.mode_vars[mode_code].get()
                new_state = not current_state
                self.ps.mode_vars[mode_code].set(new_state)
                print(f"🔄 {mode_code} is now: {'SELECTED' if new_state else 'UNSELECTED'}")
                
                # Update visual state
                self._update_option_visual_state(mode_code)
                
                # Call the original handler
                self._on_mode_selection_change()
            else:
                print(f"⚠️ Mode variable missing for {mode_code}")
                
        except Exception as e:
            print(f"❌ Error in option handler: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_option_visual_state(self, mode_code):
        """Update the visual state of an option (blue background for selected)"""
        try:
            if mode_code not in self.option_frames:
                return
                
            frame = self.option_frames[mode_code]
            is_selected = self.ps.mode_vars[mode_code].get() if mode_code in self.ps.mode_vars else False
            
            if is_selected:
                # Selected state: blue background, white text
                bg_color = '#0078d4'  # Microsoft blue
                fg_color = 'white'
            else:
                # Unselected state: white background, black text
                bg_color = 'white'
                fg_color = 'black'
            
            # Update frame background
            frame.config(bg=bg_color)
            
            # Update label background and foreground
            for child in frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=bg_color, fg=fg_color)
                    
        except Exception as e:
            print(f"⚠️ Error updating visual state for {mode_code}: {e}")
    
    def _on_mode_selection_change(self):
        """Handle mode selection change"""
        # Update display text using bound variable (state stability)
        self._update_display_text()
        
        # Get selected modes
        selected_modes = self.get_selected_processing_modes()
        print(f"🔄 Mode selection changed: {selected_modes}")
        
        # Use comprehensive live state binding refresh
        if hasattr(self.ps, 'event_handlers') and hasattr(self.ps.event_handlers, '_refresh_all_dependent_sections'):
            self.ps.event_handlers._refresh_all_dependent_sections()
        # Also notify main tab for any additional processing
        elif hasattr(self.ps.main_tab, 'on_processing_modes_changed'):
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
        
        # Update display text if UI exists
        self._update_display_text()
        
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
    
    def cleanup(self):
        """Clean up any open dropdowns - call when leaving tab or starting automation"""
        if self.menu_visible and self.mode_menu:
            print("🧹 Cleaning up open Processing dropdown before automation")
            self._hide_mode_menu()