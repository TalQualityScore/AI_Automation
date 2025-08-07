# app/src/automation/workflow_ui_components/results/action_buttons.py

import tkinter as tk
from tkinter import ttk

class ActionButtons:
    """Handles action button creation with FIXED equal sizing"""
    
    def __init__(self, theme):
        self.theme = theme
    
    def create_success_buttons(self, parent, on_open_folder, on_done):
        """Create success action buttons with FORCED equal sizing"""
        
        # Action Buttons
        button_frame = ttk.Frame(parent, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Center the buttons
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # FORCE equal sizing by using configure after creation
        folder_btn = ttk.Button(button_container, text="📁 Open Output Folder", 
                            command=on_open_folder)
        folder_btn.pack(side=tk.LEFT, padx=(0, 15), ipady=8)  # Add vertical padding
        
        done_btn = ttk.Button(button_container, text="✅ Done", 
                            command=on_done)
        done_btn.pack(side=tk.LEFT, ipady=8)  # Add vertical padding
        
        # Force both buttons to bigger size
        folder_btn.configure(width=25)  # Bigger character width
        done_btn.configure(width=25)    # Same bigger character width

    
    def create_error_buttons(self, parent, on_copy_error, on_close):
        """Create error action buttons with FIXED equal sizing"""
        
        # Error action buttons
        button_frame = ttk.Frame(parent, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # FIXED: Use EXACTLY the same ipadx for both buttons
        copy_btn = ttk.Button(button_container, text="📋 Copy Error Details", 
                             style='Secondary.TButton', command=on_copy_error)
        copy_btn.pack(side=tk.LEFT, padx=(0, 15), ipadx=25, ipady=6)
        
        close_btn = ttk.Button(button_container, text="❌ Close", 
                              style='Primary.TButton', command=on_close)
        close_btn.pack(side=tk.LEFT, ipadx=25, ipady=6)  # EXACT SAME PADDING