# app/src/automation/workflow_dialog/tab_management.py
# COMPLETE FILE - Preserves processing state when switching tabs

import tkinter as tk
from tkinter import ttk
from typing import Optional

from automation.workflow_ui_components import (
    ConfirmationTab, ProcessingTab, ResultsTab, ConfirmationData
)

class TabManager:
    """Manages tab navigation and state - WITH STATE PRESERVATION"""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.tab_buttons = {}
        self.current_tab = 0
        
        # State flags
        self.processing_started = False
        self.processing_active = False
        self.processing_complete = False
        self.processing_result = None
        
        # Tab components (initialized later)
        self.confirmation_tab = None
        self.processing_tab = None
        self.results_tab = None
        self.content_container = None
        self.confirmation_buttons = None  # Explicitly initialize as None
        
        # FIXED: Store processing state for restoration
        self.saved_processing_state = None
    
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
        """Show specified tab with state preservation for processing tab"""
        
        # FIXED: Save processing state before switching away
        if self.current_tab == 1 and self.processing_active and tab_index != 1:
            # Save the current processing state
            if self.processing_tab:
                self.saved_processing_state = {
                    'progress': self.processing_tab.progress_var.get() if self.processing_tab.progress_var else 0,
                    'step_text': self.processing_tab.step_label.cget('text') if self.processing_tab.step_label else '',
                    'counter_text': self.processing_tab.video_counter_label.cget('text') if self.processing_tab.video_counter_label else '',
                    'current_video': getattr(self.processing_tab, 'current_video', 0),
                    'total_videos': getattr(self.processing_tab, 'total_videos', 0)
                }
                print(f"📌 Saved processing state: {self.saved_processing_state}")
        
        # FIXED: Allow viewing other tabs during processing (removed lock)
        # Processing lock logic - commented out to allow navigation
        # if self.processing_active and tab_index != 1:
        #     print("🔒 Processing is active - navigation locked to Processing tab")
        #     return  # Block navigation away from processing tab while active
        
        # Clean up any existing confirmation buttons first
        if hasattr(self, 'confirmation_buttons') and self.confirmation_buttons:
            try:
                self.confirmation_buttons.destroy()
            except:
                pass
            delattr(self, 'confirmation_buttons')
        
        # Hide all existing frames
        for widget in self.content_container.winfo_children():
            widget.pack_forget()
        
        # Show selected tab
        if tab_index == 0:
            # Confirmation tab
            frame = self.confirmation_tab.create_tab()
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Button logic based on processing state
            if self.processing_complete:
                # Show read-only message when processing is complete
                self._add_readonly_message("✅ Processing completed successfully. Review results in the Results tab.")
            elif self.processing_active:
                # Show message that processing is ongoing
                self._add_readonly_message("⚙️ Processing is currently active. View progress in the Processing tab.")
            elif not self.processing_started:
                # Show normal confirmation buttons when not started
                self._add_confirmation_buttons()
            else:
                # Processing has started but not active (shouldn't happen, but safety)
                self._add_readonly_message("Processing has been initiated.")
            
        elif tab_index == 1:
            # Processing tab
            frame = self.processing_tab.create_tab(self.dialog.confirmation_data.estimated_time)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # FIXED: Restore saved state if returning to processing tab
            if self.processing_active and self.saved_processing_state:
                self._restore_processing_state()
            
            # Processing tab buttons based on state
            if self.processing_complete:
                self._add_completed_processing_buttons(frame)
            elif self.processing_active:
                self._add_active_processing_buttons(frame)
            else:
                # Processing tab accessed but not active (view-only)
                self._add_inactive_processing_message(frame)
            
        elif tab_index == 2:
            # Results tab
            frame = self.results_tab.create_tab()
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Restore results if available
            if self.processing_result and self.processing_complete:
                self._restore_results()
        
        # Update tab button states
        self._update_tab_buttons(tab_index)
        self.current_tab = tab_index
    
    def _restore_processing_state(self):
        """FIXED: Restore the saved processing state"""
        if not self.saved_processing_state or not self.processing_tab:
            return
        
        state = self.saved_processing_state
        
        # Restore progress bar
        if self.processing_tab.progress_var:
            self.processing_tab.progress_var.set(state['progress'])
        
        # Restore progress label
        if self.processing_tab.progress_label:
            self.processing_tab.progress_label.config(text=f"{int(state['progress'])}%")
        
        # Restore step label
        if self.processing_tab.step_label:
            self.processing_tab.step_label.config(text=state['step_text'])
        
        # Restore video counter
        if self.processing_tab.video_counter_label and state['counter_text']:
            self.processing_tab.video_counter_label.config(text=state['counter_text'])
        
        # Restore internal counters
        self.processing_tab.current_video = state['current_video']
        self.processing_tab.total_videos = state['total_videos']
        
        print(f"📌 Restored processing state successfully")
    
    def _add_confirmation_buttons(self):
        """UPDATED: Add action buttons to confirmation tab with transition support"""
        button_frame = ttk.Frame(self.dialog.root, style='White.TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=(0, 30), side=tk.BOTTOM)
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # Cancel button
        ttk.Button(button_container, text="❌ CANCEL", style='Secondary.TButton',
                  command=self.dialog._on_cancel).pack(side=tk.LEFT, padx=(0, 15))
        
        # UPDATED: Confirm button with new handler
        confirm_btn = ttk.Button(button_container, text="✅ CONFIRM & RUN", 
                                style='Accent.TButton', 
                                command=self._on_confirm_with_transitions)
        confirm_btn.pack(side=tk.LEFT)
        confirm_btn.focus_set()
        
        self.confirmation_buttons = button_frame
    
    def _on_confirm_with_transitions(self):
        """NEW: Handle confirm with transition settings"""
        # Get the transition setting from confirmation tab
        use_transitions = self.confirmation_tab.get_transition_setting() if hasattr(self.confirmation_tab, 'get_transition_setting') else True
        
        # Store the transition setting for processing
        self.dialog.use_transitions = use_transitions
        
        print(f"🎬 Starting processing with transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
        
        # Call the original confirm handler
        self.dialog._on_confirm()
    
    def _add_readonly_message(self, message):
        """Add read-only message for completed tabs"""
        message_frame = ttk.Frame(self.dialog.root, style='White.TFrame')
        message_frame.pack(fill=tk.X, padx=40, pady=(0, 30), side=tk.BOTTOM)
        
        ttk.Label(message_frame, text=message, style='Body.TLabel',
                 font=('Segoe UI', 11, 'italic'),
                 foreground=self.dialog.theme.colors['text_secondary']).pack()
        
        self.confirmation_buttons = message_frame
    
    def _add_active_processing_buttons(self, parent):
        """Add cancel button for active processing"""
        cancel_frame = ttk.Frame(parent, style='White.TFrame')
        cancel_frame.pack(fill=tk.X, pady=30)
        
        cancel_container = ttk.Frame(cancel_frame, style='White.TFrame')
        cancel_container.pack()
        
        self.processing_tab.cancel_btn = ttk.Button(cancel_container, text="❌ Cancel Processing", 
                                                   style='Secondary.TButton',
                                                   command=self.dialog._on_cancel)
        self.processing_tab.cancel_btn.pack()
    
    def _add_completed_processing_buttons(self, parent):
        """Add buttons for completed processing tab"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_container = ttk.Frame(info_frame, style='White.TFrame')
        info_container.pack()
        
        ttk.Label(info_container, text="✅ Processing completed successfully!", 
                 style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
                 foreground=self.dialog.theme.colors['success']).pack(pady=10)
        
        ttk.Button(info_container, text="📊 View Results", 
                  style='Accent.TButton',
                  command=lambda: self.show_tab(2)).pack()
    
    def _add_inactive_processing_message(self, parent):
        """Add message for inactive processing tab (view-only)"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_container = ttk.Frame(info_frame, style='White.TFrame')
        info_container.pack()
        
        ttk.Label(info_container, text="⏸️ Processing not currently active", 
                 style='Body.TLabel', font=('Segoe UI', 11),
                 foreground=self.dialog.theme.colors['text_secondary']).pack(pady=10)
        
        ttk.Label(info_container, text="Return to Confirmation tab to start processing", 
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                 foreground=self.dialog.theme.colors['text_secondary']).pack()
    
    def _update_tab_buttons(self, active_tab):
        """Update tab button states - FIXED to allow navigation during processing"""
        for idx, btn in self.tab_buttons.items():
            if idx == active_tab:
                # Active tab
                btn.configure(bg=self.dialog.theme.colors['tab_active'], 
                             fg=self.dialog.theme.colors['text_primary'],
                             state='normal')
            else:
                # Tab availability logic
                if self.processing_complete:
                    # After processing: all tabs accessible (view-only for confirmation/processing)
                    btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                 fg=self.dialog.theme.colors['text_primary'],
                                 state='normal')
                elif self.processing_active:
                    # FIXED: Allow navigation to all tabs even during processing
                    btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                 fg=self.dialog.theme.colors['text_primary'],
                                 state='normal')
                elif self.processing_started:
                    # Processing started but not active: allow back to processing tab
                    if idx <= 1:  # Confirmation and Processing accessible
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_primary'],
                                     state='normal')
                    else:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_secondary'], 
                                     state='disabled')
                else:
                    # Before processing: only current and previous tabs
                    if idx <= active_tab:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_primary'],
                                     state='normal')
                    else:
                        btn.configure(bg=self.dialog.theme.colors['tab_inactive'], 
                                     fg=self.dialog.theme.colors['text_secondary'], 
                                     state='disabled')
    
    def on_confirm_clicked(self):
        """Handle confirm button - start processing with proper state management"""
        # Mark that processing has started and is now active
        self.processing_started = True
        self.processing_active = True
        
        # Get transition setting if available
        use_transitions = getattr(self.dialog, 'use_transitions', True)
        
        # Clean up confirmation buttons
        if hasattr(self, 'confirmation_buttons') and self.confirmation_buttons:
            try:
                self.confirmation_buttons.destroy()
            except:
                pass
            delattr(self, 'confirmation_buttons')
        
        # Switch to processing tab
        self.show_tab(1)
        
        # Start processing via the processing manager with transition setting
        if hasattr(self.dialog, 'processing_manager') and self.dialog.processing_manager:
            # The processing manager will handle calling the callback with proper arguments
            self.dialog.processing_manager.start_processing(
                lambda progress_callback: self.dialog.processing_callback(
                    self.dialog.confirmation_data, 
                    progress_callback,
                    use_transitions=use_transitions
                ),
                self.dialog.confirmation_data.estimated_time
            )
    
    def show_results(self, result):
        """Show results in the results tab"""
        self.on_processing_complete(result)
        self.show_tab(2)
    
    def on_processing_complete(self, result):
        """Handle processing completion with proper state updates"""
        self.processing_active = False
        self.processing_complete = True
        self.processing_result = result
        
        # Clear saved processing state
        self.saved_processing_state = None
        
        # Update processing tab to show completion
        if hasattr(self.processing_tab, 'update_progress'):
            if result.success:
                self.processing_tab.update_progress(100, "✅ Processing completed successfully!")
            else:
                self.processing_tab.update_progress(100, "❌ Processing failed!")
    
    def _restore_results(self):
        """Restore results tab with saved data - FIXED with proper callbacks"""
        if not self.processing_result:
            print("⚠️ No processing result to restore")
            return
        
        print(f"📊 Restoring results tab with saved result: success={self.processing_result.success}")
        
        # Define the callback functions for results tab
        def on_open_folder():
            """Open the output folder"""
            try:
                import os
                import subprocess
                if self.processing_result and self.processing_result.output_folder:
                    if os.path.exists(self.processing_result.output_folder):
                        subprocess.Popen(f'explorer "{self.processing_result.output_folder}"')
                        print(f"📁 Opened folder: {self.processing_result.output_folder}")
            except Exception as e:
                print(f"❌ Error opening folder: {e}")
        
        def on_done():
            """Handle done button - close dialog successfully"""
            print("✅ Done clicked - closing workflow")
            if self.dialog:
                self.dialog._on_success_close()
        
        def on_copy_error():
            """Copy error details to clipboard"""
            try:
                import pyperclip
                if self.processing_result and self.processing_result.error_message:
                    error_text = f"Error: {self.processing_result.error_message}\n"
                    if self.processing_result.error_solution:
                        error_text += f"Solution: {self.processing_result.error_solution}"
                    pyperclip.copy(error_text)
                    print("📋 Error details copied to clipboard")
            except Exception as e:
                print(f"❌ Error copying to clipboard: {e}")
        
        def on_close():
            """Handle close button on error - close dialog"""
            print("❌ Close clicked after error")
            if self.dialog:
                self.dialog._on_error_close()
        
        # Show results with proper callbacks based on success/failure
        if self.processing_result.success:
            self.results_tab.show_success_results(
                self.processing_result,
                on_open_folder,  # ADDED: Required callback
                on_done          # ADDED: Required callback
            )
        else:
            self.results_tab.show_error_results(
                self.processing_result,
                on_copy_error,   # ADDED: Required callback
                on_close         # ADDED: Required callback
            )