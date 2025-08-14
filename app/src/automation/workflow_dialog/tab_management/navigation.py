# app/src/automation/workflow_dialog/tab_management/navigation.py
"""Navigation Handler - Manages tab navigation and display"""

import tkinter as tk
from tkinter import ttk

class NavigationHandler:
    """Handles tab navigation logic"""
    
    def __init__(self, tab_manager):
        self.tm = tab_manager
    
    def create_tab_navigation(self, parent):
        """Create tab navigation bar"""
        tab_frame = ttk.Frame(parent, style='Tabs.TFrame')
        tab_frame.pack(fill=tk.X, padx=40, pady=(20, 0))
        
        tabs = [
            ("1. Confirmation", 0),
            ("2. Processing", 1),
            ("3. Results", 2)
        ]
        
        for tab_name, tab_index in tabs:
            btn = tk.Button(
                tab_frame, 
                text=tab_name, 
                font=('Segoe UI', 11),
                bg=self.tm.dialog.theme.colors['tab_inactive'], 
                fg=self.tm.dialog.theme.colors['text_primary'],
                activebackground=self.tm.dialog.theme.colors['tab_active'],
                activeforeground=self.tm.dialog.theme.colors['text_primary'],
                relief='flat', 
                borderwidth=0, 
                padx=20, 
                pady=10,
                command=lambda idx=tab_index: self.tm.show_tab(idx)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 1))
            self.tm.tab_buttons[tab_index] = btn
    
    def show_tab(self, tab_index):
        """Show specified tab with state preservation"""
        
        # Save processing state if switching away from processing tab
        if self.tm.current_tab == 1 and self.tm.processing_active and tab_index != 1:
            self.tm.saved_processing_state = self.tm.state_handler.save_processing_state()
        
        # Clean up any existing confirmation buttons
        self.tm.button_handler.cleanup_confirmation_buttons()
        
        # Hide all existing frames
        for widget in self.tm.content_container.winfo_children():
            widget.pack_forget()
        
        # Show selected tab
        if tab_index == 0:
            self._show_confirmation_tab()
        elif tab_index == 1:
            self._show_processing_tab()
        elif tab_index == 2:
            self._show_results_tab()
        
        # Update tab button states
        self._update_tab_buttons(tab_index)
        self.tm.current_tab = tab_index
    
    def _show_confirmation_tab(self):
        """Display confirmation tab with appropriate buttons"""
        frame = self.tm.confirmation_tab.create_tab()
        frame.pack(fill=tk.BOTH, expand=True)
        
        print(f"DEBUG: _show_confirmation_tab called")
        print(f"DEBUG: processing_complete = {self.tm.processing_complete}")
        print(f"DEBUG: processing_active = {self.tm.processing_active}")
        print(f"DEBUG: processing_started = {self.tm.processing_started}")
        
        # Determine which buttons to show
        if self.tm.processing_complete:
            self.tm.button_handler.add_readonly_message(
                "✅ Processing completed successfully. Review results in the Results tab."
            )
        elif self.tm.processing_active:
            self.tm.button_handler.add_readonly_message(
                "⚙️ Processing is currently active. View progress in the Processing tab."
            )
        elif not self.tm.processing_started:
            print("DEBUG: Adding confirmation buttons (not started)")
            # IMPORTANT: Call the NEW overlay method, not the old one
            self.tm.dialog.root.after(100, self.tm.button_handler.add_confirmation_buttons_overlay)
        else:
            self.tm.button_handler.add_readonly_message("Processing has been initiated.")

    def _force_button_visibility(self):
        """Force buttons to be visible after UI settles"""
        if hasattr(self.tm, 'confirmation_buttons') and self.tm.confirmation_buttons:
            # Force the button frame to be visible
            self.tm.confirmation_buttons.lift()
            self.tm.confirmation_buttons.pack_configure(side=tk.BOTTOM, fill=tk.X, padx=40, pady=(0, 30))
            
            # Update the UI
            self.tm.dialog.root.update_idletasks()
            self.tm.dialog.root.update()
            
            # Debug
            print(f"DEBUG: Forced button visibility")
            print(f"  Exists: {self.tm.confirmation_buttons.winfo_exists()}")
            print(f"  Visible: {self.tm.confirmation_buttons.winfo_viewable()}")
            print(f"  Geometry: {self.tm.confirmation_buttons.winfo_geometry()}")

    def _show_processing_tab(self):
        """Display processing tab"""
        frame = self.tm.processing_tab.create_tab(self.tm.dialog.confirmation_data.estimated_time)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Restore saved state if returning to active processing
        if self.tm.processing_active and self.tm.saved_processing_state:
            self.tm.state_handler.restore_processing_state()
        
        # Add appropriate buttons/messages
        if self.tm.processing_complete:
            self.tm.button_handler.add_completed_processing_buttons(frame)
        elif self.tm.processing_active:
            self.tm.button_handler.add_active_processing_buttons(frame)
        else:
            self.tm.button_handler.add_inactive_processing_message(frame)
    
    def _show_results_tab(self):
        """Display results tab"""
        frame = self.tm.results_tab.create_tab()
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Restore results if available
        if self.tm.processing_result and self.tm.processing_complete:
            self.tm.state_handler.restore_results()
    
    def _update_tab_buttons(self, active_tab):
        """Update tab button states"""
        for idx, btn in self.tm.tab_buttons.items():
            if idx == active_tab:
                # Active tab
                btn.configure(
                    bg=self.tm.dialog.theme.colors['tab_active'], 
                    fg=self.tm.dialog.theme.colors['text_primary'],
                    state='normal'
                )
            else:
                # Determine if tab should be enabled
                if self.tm.processing_complete:
                    # All tabs accessible after completion
                    btn.configure(
                        bg=self.tm.dialog.theme.colors['tab_inactive'], 
                        fg=self.tm.dialog.theme.colors['text_primary'],
                        state='normal'
                    )
                elif self.tm.processing_active:
                    # Allow navigation during processing
                    btn.configure(
                        bg=self.tm.dialog.theme.colors['tab_inactive'], 
                        fg=self.tm.dialog.theme.colors['text_primary'],
                        state='normal'
                    )
                elif self.tm.processing_started:
                    # Processing started but not active
                    if idx <= 1:
                        btn.configure(
                            bg=self.tm.dialog.theme.colors['tab_inactive'], 
                            fg=self.tm.dialog.theme.colors['text_primary'],
                            state='normal'
                        )
                    else:
                        btn.configure(
                            bg=self.tm.dialog.theme.colors['tab_inactive'], 
                            fg=self.tm.dialog.theme.colors['text_secondary'], 
                            state='disabled'
                        )
                else:
                    # Before processing: only current and previous tabs
                    if idx <= active_tab:
                        btn.configure(
                            bg=self.tm.dialog.theme.colors['tab_inactive'], 
                            fg=self.tm.dialog.theme.colors['text_primary'],
                            state='normal'
                        )
                    else:
                        btn.configure(
                            bg=self.tm.dialog.theme.colors['tab_inactive'], 
                            fg=self.tm.dialog.theme.colors['text_secondary'], 
                            state='disabled'
                        )
    def refresh_theme(self):
        """Refresh theme for all tab buttons"""
        try:
            # Update all tab button colors for current theme
            for idx, btn in self.tm.tab_buttons.items():
                if idx == self.tm.current_tab:
                    # Active tab
                    btn.configure(
                        bg=self.tm.dialog.theme.colors['tab_active'],
                        fg=self.tm.dialog.theme.colors['text_primary'],
                        activebackground=self.tm.dialog.theme.colors['tab_active'],
                        activeforeground=self.tm.dialog.theme.colors['text_primary']
                    )
                else:
                    # Inactive tab  
                    btn.configure(
                        bg=self.tm.dialog.theme.colors['tab_inactive'],
                        fg=self.tm.dialog.theme.colors['text_primary'],
                        activebackground=self.tm.dialog.theme.colors['tab_active'],
                        activeforeground=self.tm.dialog.theme.colors['text_primary']
                    )
            print("✅ Tab theme refreshed successfully")
        except Exception as e:
            print(f"⚠️ Error refreshing tab theme: {e}")
