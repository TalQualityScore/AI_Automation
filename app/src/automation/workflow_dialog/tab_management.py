# app/src/automation/workflow_dialog/tab_management.py - FIXED VERSION
import tkinter as tk
from tkinter import ttk

from ..workflow_ui_components import ConfirmationTab, ProcessingTab, ResultsTab
from ..workflow_data_models import ConfirmationData

class TabManager:
    """Handles tab navigation, switching, and content management - FIXED"""
    
    def __init__(self, dialog_controller):
        self.dialog = dialog_controller
        self.current_tab = 0
        self.tab_buttons = {}
        self.content_container = None
        
        # Tab components
        self.confirmation_tab = None
        self.processing_tab = None
        self.results_tab = None
        
        # State tracking
        self.processing_started = False
        self.processing_complete = False
        
        # FIXED: Store processing results for tab restoration
        self.processing_result = None
    
    def create_tab_navigation(self, parent):
        """Create tab navigation buttons"""
        tab_frame = ttk.Frame(parent, style='White.TFrame')
        tab_frame.pack(fill=tk.X, padx=40, pady=(20, 0))
        
        tabs = [
            ("1. Confirmation", 0),
            ("2. Processing", 1),
            ("3. Results", 2)
        ]
        
        for tab_name, tab_index in tabs:
            btn = tk.Button(tab_frame, text=tab_name, font=('Segoe UI', 11),
                           bg=self.dialog.theme.colors['tab_inactive'], 
                           fg=self.dialog.theme.colors['text_primary'],
                           relief='flat', borderwidth=0, padx=20, pady=10,
                           command=lambda idx=tab_index: self.show_tab(idx))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 1))
            self.tab_buttons[tab_index] = btn
    
    def create_content_area(self, parent):
        """Create content container for tabs"""
        self.content_container = ttk.Frame(parent, style='White.TFrame')
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
    
    def initialize_tabs(self, confirmation_data: ConfirmationData, theme):
        """Initialize all tab components"""
        # Tab 1: Confirmation
        self.confirmation_tab = ConfirmationTab(
            self.content_container, 
            confirmation_data, 
            theme
        )
        
        # Tab 2: Processing
        self.processing_tab = ProcessingTab(self.content_container, theme)
        
        # Tab 3: Results
        self.results_tab = ResultsTab(self.content_container, theme)
    
    def show_tab(self, tab_index):
        """Show specified tab and update navigation - FIXED for completed processing"""
        # Clean up any existing confirmation buttons first
        if hasattr(self, 'confirmation_buttons'):
            self.confirmation_buttons.destroy()
            delattr(self, 'confirmation_buttons')
        
        # Hide all existing frames
        for widget in self.content_container.winfo_children():
            widget.pack_forget()
        
        # Show selected tab
        if tab_index == 0:
            # Confirmation tab
            frame = self.confirmation_tab.create_tab()
            frame.pack(fill=tk.BOTH, expand=True)
            
            # FIXED: Only add buttons if processing hasn't completed
            if not self.processing_complete:
                self._add_confirmation_buttons()
            else:
                # Show read-only message
                self._add_readonly_message("Confirmation completed. Processing has finished successfully.")
            
        elif tab_index == 1:
            # Processing tab
            frame = self.processing_tab.create_tab(self.dialog.confirmation_data.estimated_time)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # FIXED: Add appropriate buttons based on processing state
            if self.processing_complete:
                self._add_readonly_processing_buttons(frame)
            else:
                self._add_processing_buttons(frame)
            
        elif tab_index == 2:
            # Results tab
            frame = self.results_tab.create_tab()
            frame.pack(fill=tk.BOTH, expand=True)
            
            # FIXED: If we have results, show them again
            if self.processing_result and self.processing_complete:
                self._restore_results()
        
        # Update tab button states
        self._update_tab_buttons(tab_index)
        self.current_tab = tab_index
    
    def _add_confirmation_buttons(self):
        """Add action buttons to confirmation tab"""
        # Create button frame at root level, not inside tab content
        button_frame = ttk.Frame(self.dialog.root, style='White.TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=(0, 30), side=tk.BOTTOM)
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        ttk.Button(button_container, text="❌ CANCEL", style='Secondary.TButton',
                  command=self.dialog._on_cancel).pack(side=tk.LEFT, padx=(0, 15))
        
        confirm_btn = ttk.Button(button_container, text="✅ CONFIRM & RUN", 
                                style='Accent.TButton', command=self.dialog._on_confirm)
        confirm_btn.pack(side=tk.LEFT)
        confirm_btn.focus_set()
        
        # Store reference for cleanup
        self.confirmation_buttons = button_frame
    
    def _add_readonly_message(self, message):
        """Add read-only message for completed tabs"""
        message_frame = ttk.Frame(self.dialog.root, style='White.TFrame')
        message_frame.pack(fill=tk.X, padx=40, pady=(0, 30), side=tk.BOTTOM)
        
        ttk.Label(message_frame, text=message, style='Body.TLabel',
                 font=('Segoe UI', 10, 'italic'),
                 foreground=self.dialog.theme.colors['text_secondary']).pack()
        
        # Store reference for cleanup
        self.confirmation_buttons = message_frame
    
    def _add_processing_buttons(self, parent):
        """Add cancel button to processing tab"""
        cancel_frame = ttk.Frame(parent, style='White.TFrame')
        cancel_frame.pack(fill=tk.X, pady=30)
        
        cancel_container = ttk.Frame(cancel_frame, style='White.TFrame')
        cancel_container.pack()
        
        self.processing_tab.cancel_btn = ttk.Button(cancel_container, text="❌ Cancel", 
                                                   style='Secondary.TButton',
                                                   command=self.dialog._on_cancel)
        self.processing_tab.cancel_btn.pack()
    
    def _add_readonly_processing_buttons(self, parent):
        """Add read-only buttons for completed processing tab"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_container = ttk.Frame(info_frame, style='White.TFrame')
        info_container.pack()
        
        # FIXED: Show completion message instead of cancel button
        ttk.Label(info_container, text="✅ Processing completed successfully!", 
                 style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
                 foreground=self.dialog.theme.colors['success']).pack(pady=10)
        
        # View Results button
        ttk.Button(info_container, text="📊 View Results", 
                  style='Accent.TButton',
                  command=lambda: self.show_tab(2)).pack()
    
    def _update_tab_buttons(self, active_tab):
        """Update tab button appearance and enable/disable properly - FIXED"""
        for idx, btn in self.tab_buttons.items():
            if idx == active_tab:
                # Active tab
                btn.configure(bg=self.dialog.theme.colors['tab_active'], 
                             fg=self.dialog.theme.colors['text_primary'],
                             state='normal')
            else:
                # FIXED: Different behavior based on processing state
                if self.processing_complete:
                    # After processing: all tabs are accessible for viewing
                    btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                 fg=self.dialog.theme.colors['text_primary'],
                                 state='normal')
                elif self.processing_started:
                    # During processing: only allow current and previous tabs
                    if idx <= active_tab:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_primary'],
                                     state='normal')
                    else:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_secondary'], 
                                     state='disabled')
                else:
                    # Before processing: only allow current and previous tabs
                    if idx <= active_tab:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_primary'],
                                     state='normal')
                    else:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_secondary'], 
                                     state='disabled')
    
    def on_confirm_clicked(self):
        """Handle confirm button - start processing"""
        # Mark that processing has started
        self.processing_started = True
        
        # Clean up confirmation buttons before switching tabs
        if hasattr(self, 'confirmation_buttons'):
            self.confirmation_buttons.destroy()
            delattr(self, 'confirmation_buttons')
        
        self.show_tab(1)  # Switch to processing tab
        
        # Start processing via the processing manager
        self.dialog.processing_manager.start_processing(
            self.dialog.processing_callback,
            self.dialog.confirmation_data.estimated_time
        )
    
    def on_processing_complete(self, result):
        """Handle processing completion - FIXED to store results"""
        self.processing_complete = True
        self.processing_result = result  # FIXED: Store result for tab switching
        
        # Update processing tab to show completion
        if hasattr(self.processing_tab, 'update_progress'):
            if result.success:
                self.processing_tab.update_progress(100, "✅ Processing completed successfully!")
            else:
                self.processing_tab.update_progress(100, "❌ Processing failed!")
        
        # Update tab navigation to allow access to all tabs
        self._update_tab_buttons(self.current_tab)
        
        # Auto-advance to results after 2 seconds
        self.dialog.root.after(2000, lambda: self.show_results(result))
    
    def show_results(self, result):
        """Show results tab with data - FIXED"""
        self.show_tab(2)
        self._display_results(result)
    
    def _display_results(self, result):
        """Display results in the results tab - FIXED"""
        if result.success:
            from ..workflow_ui_components import open_folder
            self.results_tab.show_success_results(
                result,
                on_open_folder=open_folder,
                on_done=self.dialog._on_success_close
            )
        else:
            from ..workflow_ui_components import copy_to_clipboard
            self.results_tab.show_error_results(
                result,
                on_copy_error=lambda msg: copy_to_clipboard(self.dialog.root, msg),
                on_close=self.dialog._on_error_close
            )
    
    def _restore_results(self):
        """Restore results when switching back to results tab - FIXED"""
        if self.processing_result:
            self._display_results(self.processing_result)