# app/src/automation/workflow_dialog/tab_management/main.py
"""Main TabManager class - Core tab management logic"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

# Use relative imports to avoid path issues
try:
    # Try relative import first (preferred)
    from ...workflow_ui_components import (
        ConfirmationTab, ProcessingTab, ResultsTab, ConfirmationData
    )
except ImportError:
    # Fallback to absolute import
    from app.src.automation.workflow_ui_components import (
        ConfirmationTab, ProcessingTab, ResultsTab, ConfirmationData
    )

# Import handler modules from current package
from .button_handler import ButtonHandler
from .state_handler import StateHandler
from .navigation import NavigationHandler

class TabManager:
    """Manages tab navigation and state - Modular architecture"""
    
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
        self.confirmation_buttons = None
        
        # Handler modules
        self.button_handler = ButtonHandler(self)
        self.state_handler = StateHandler(self)
        self.navigation = NavigationHandler(self)
        
        # Store processing state for restoration
        self.saved_processing_state = None
    
    def create_tab_navigation(self, parent):
        """Create tab navigation bar"""
        self.navigation.create_tab_navigation(parent)
    
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
        
        # FORCE initial state to ensure buttons show
        self.processing_started = False
        self.processing_active = False
        self.processing_complete = False
        
        # Show initial tab with buttons
        print("DEBUG: Initializing tabs - showing tab 0 with buttons")
        self.show_tab(0)
    
    def show_tab(self, tab_index):
        """Show specified tab"""
        self.navigation.show_tab(tab_index)
    
    def refresh_theme(self):
        """Refresh theme for all tabs and components"""
        # Refresh confirmation tab
        if self.confirmation_tab and hasattr(self.confirmation_tab, 'refresh_theme'):
            self.confirmation_tab.refresh_theme()
        
        # Refresh processing tab
        if self.processing_tab and hasattr(self.processing_tab, 'refresh_theme'):
            self.processing_tab.refresh_theme()
        
        # Refresh results tab
        if self.results_tab and hasattr(self.results_tab, 'refresh_theme'):
            self.results_tab.refresh_theme()
        
        # Refresh tab navigation
        if self.navigation and hasattr(self.navigation, 'refresh_theme'):
            self.navigation.refresh_theme()
        
        # Refresh button handler
        if self.button_handler and hasattr(self.button_handler, 'refresh_theme'):
            self.button_handler.refresh_theme()
    
    def on_confirm_clicked(self):
        """Handle confirm button - start processing"""
        # Mark that processing has started and is now active
        self.processing_started = True
        self.processing_active = True
        
        # Get transition setting if available
        use_transitions = getattr(self.dialog, 'use_transitions', True)
        
        # Clean up confirmation buttons
        self.button_handler.cleanup_confirmation_buttons()
        
        # Switch to processing tab
        self.show_tab(1)
        
        # Start processing via the processing manager
        if hasattr(self.dialog, 'processing_manager') and self.dialog.processing_manager:
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