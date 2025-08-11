# app/src/automation/api_clients/account_mapper/dialog_modules/dialog_layout.py
"""
Dialog Layout Module
Manages dialog window layout and positioning
"""

import tkinter as tk
from .dialog_constants import DialogConstants

class DialogLayout:
    """Manages dialog layout and window properties"""
    
    def __init__(self):
        self.constants = DialogConstants
    
    def setup_window(self, dialog):
        """Setup dialog window properties"""
        dialog.title(self.constants.WINDOW_TITLE)
        dialog.geometry(f"{self.constants.WINDOW_WIDTH}x{self.constants.WINDOW_HEIGHT}")
        dialog.resizable(False, False)
        dialog.configure(bg=self.constants.BG_COLOR)
        
        # Center dialog
        self.center_window(dialog)
        
        # Make dialog modal and on top
        dialog.attributes('-topmost', True)
        dialog.focus_force()
    
    def center_window(self, dialog):
        """Center the dialog on screen"""
        x = (dialog.winfo_screenwidth() // 2) - (self.constants.WINDOW_WIDTH // 2)
        y = (dialog.winfo_screenheight() // 2) - (self.constants.WINDOW_HEIGHT // 2)
        dialog.geometry(f"{self.constants.WINDOW_WIDTH}x{self.constants.WINDOW_HEIGHT}+{x}+{y}")
    
    def create_main_frame(self, dialog):
        """Create the main content frame"""
        main_frame = tk.Frame(
            dialog, 
            bg=self.constants.BG_COLOR, 
            padx=30, 
            pady=25
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        return main_frame
    
    def create_selection_frame(self, parent_frame):
        """Create frame for selection dropdowns"""
        selection_frame = tk.Frame(parent_frame, bg=self.constants.BG_COLOR)
        selection_frame.pack(fill=tk.X, pady=(0, 25))
        return selection_frame