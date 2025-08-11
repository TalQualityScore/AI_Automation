# app/src/automation/api_clients/account_mapper/fallback_dialog.py - REFACTORED
"""
Fallback Selection Dialog - REFACTORED
Now uses modular components for better organization
"""

import tkinter as tk
from typing import Tuple
from .dialog_modules import (
    DialogBuilder, DialogLayout, EventHandler,
    SelectionManager, DialogConstants
)

class FallbackSelectionDialog:
    """Shows verification dialog when account/platform detection needs confirmation"""
    
    def __init__(self):
        # Use constants from module
        self.account_mapping = DialogConstants.ACCOUNT_MAPPING
        self.platform_mapping = DialogConstants.PLATFORM_MAPPING
    
    def show_fallback_selection(self, card_title: str, detected_account: str = None, 
                               detected_platform: str = None, card_url: str = None) -> Tuple[str, str]:
        """
        Show verification dialog for account/platform confirmation - REFACTORED
        Now ~50 lines instead of 215 lines
        
        Args:
            card_title: The Trello card title for context
            detected_account: Previously detected account (if any)
            detected_platform: Previously detected platform (if any)
            card_url: The Trello card URL to display (optional)
            
        Returns:
            Tuple of (selected_account, selected_platform)
        """
        
        print(f"🎬 VERIFICATION DIALOG: Showing for '{card_title}'")
        print(f"🎬 VERIFICATION DIALOG: Detected account='{detected_account}', platform='{detected_platform}'")
        
        # Create root and dialog
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        dialog = tk.Toplevel(root)
        
        # Setup layout
        layout = DialogLayout()
        layout.setup_window(dialog)
        main_frame = layout.create_main_frame(dialog)
        
        # Initialize managers
        builder = DialogBuilder(dialog)
        selection_manager = SelectionManager()
        event_handler = EventHandler(selection_manager)
        
        # Build UI components
        builder.create_header(main_frame)
        builder.create_context_label(main_frame, card_url, card_title)
        
        # Create selection frame
        selection_frame = layout.create_selection_frame(main_frame)
        
        # Create dropdowns
        account_var, account_combo = builder.create_dropdown(
            selection_frame,
            "Account:",
            DialogConstants.get_account_options(),
            DialogConstants.get_default_account(detected_account)
        )
        
        platform_var, platform_combo = builder.create_dropdown(
            selection_frame,
            "Platform:",
            DialogConstants.get_platform_options(),
            DialogConstants.get_default_platform(detected_platform)
        )
        
        # Store variables in selection manager
        selection_manager.set_variables(account_var, platform_var)
        
        # Create separator
        builder.create_separator(main_frame)
        
        # Create Apply button
        builder.create_apply_button(main_frame, selection_manager.process_selection)
        
        # Setup event handlers
        event_handler.setup_close_handler(dialog)
        
        # Poll for result
        result = event_handler.poll_for_result(root, dialog)
        
        # Cleanup
        try:
            dialog.destroy()
        except:
            pass
        try:
            root.destroy()
        except:
            pass
        
        # Extract final values
        selected_account = result.get("account", "TR")
        selected_platform = result.get("platform", "FB")
        action = result.get("action", "timeout")
        
        print(f"🎯 VERIFICATION RESULT: Account='{selected_account}', Platform='{selected_platform}', Action='{action}'")
        
        return selected_account, selected_platform