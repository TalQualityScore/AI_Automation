# app/src/automation/api_clients/account_mapper/dialog_modules/event_handler.py
"""
Event Handler Module
Handles dialog events and user interactions
"""

import tkinter as tk
from tkinter import messagebox
import time
from .dialog_constants import DialogConstants

class EventHandler:
    """Handles dialog events and polling"""
    
    def __init__(self, selection_manager):
        self.selection_manager = selection_manager
        self.constants = DialogConstants
    
    def setup_close_handler(self, dialog):
        """Setup window close button handler"""
        def on_window_close():
            response = messagebox.askyesno(
                "Selection Required",
                "You must verify the account and platform to continue.\n\n"
                "Close anyway? This will exit the entire program.",
                default='no'
            )
            
            if response:
                self.selection_manager.handle_window_close()
            # If no, dialog stays open
        
        dialog.protocol("WM_DELETE_WINDOW", on_window_close)
    
    def poll_for_result(self, root, dialog):
        """Poll for user selection result"""
        print("🔍 Starting verification dialog polling...")
        start_time = time.time()
        
        while not self.selection_manager.is_done():
            # Check timeout
            if (time.time() - start_time) > self.constants.MAX_WAIT_TIME:
                print("⏰ Verification dialog timed out")
                self.selection_manager.result = {
                    "account": "TR", 
                    "platform": "FB", 
                    "action": "timeout", 
                    "done": True
                }
                break
            
            try:
                root.update()  # Process events
                time.sleep(self.constants.POLL_INTERVAL)
            except tk.TclError:
                # Dialog was closed
                break
        
        return self.selection_manager.get_result()